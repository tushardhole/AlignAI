"""AlignAI desktop entrypoint: constructs adapters and starts the Qt shell."""

from __future__ import annotations

import logging
import sys

from agents import set_default_openai_api, set_default_openai_client
from openai import AsyncOpenAI
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

from alignai.agents.align_ai_runner import AlignAiAgentRunner
from alignai.application.create_alignment import CreateAlignment
from alignai.application.handle_telegram_message import HandleTelegramMessage
from alignai.application.list_alignments import ListAlignments
from alignai.application.set_base_documents import SetBaseDocuments
from alignai.infra.app_paths import resolve_config_dir, resolve_data_dir
from alignai.infra.document_repository import FilesystemDocumentRepository
from alignai.infra.job_fetcher_chain import ChainedJobFetcher
from alignai.infra.json_settings_store import JsonSettingsStore
from alignai.infra.keyring_secrets import KeyringSecrets
from alignai.infra.pdf_input_pypdf import PdfDocxTextExtractor
from alignai.infra.pdf_render_chromium import ChromiumPdfRenderer
from alignai.infra.sqlite_alignment_repository import SqliteAlignmentRepository
from alignai.infra.telegram_bridge import TelegramBotService
from alignai.infra.text_cleanup import clean
from alignai.ui.blocking_runner_thread import BlockingRunnerThread
from alignai.ui.main_window import MainDeps, MainWindow


def _build_create_alignment(
    settings_store: JsonSettingsStore,
    secrets: KeyringSecrets,
    alignment_repo: SqliteAlignmentRepository,
    pdf_renderer: ChromiumPdfRenderer,
    data_dir: object,
) -> CreateAlignment:
    base_url = settings_store.get("llm_base_url") or "https://api.openai.com/v1"
    model = settings_store.get("llm_model") or "gpt-4o-mini"
    api_key = secrets.get("llm_api_key") or "dummy-key"
    openai_client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    set_default_openai_client(openai_client, use_for_tracing=False)
    set_default_openai_api("chat_completions")
    runner = AlignAiAgentRunner(openai_client, model, settings_store)
    from pathlib import Path

    return CreateAlignment(
        runner,
        alignment_repo,
        pdf_renderer,
        Path(str(data_dir)),
        sanitize_text=clean,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    qt_app = QApplication(sys.argv)
    qt_app.setStyle("Fusion")
    from alignai.ui.styles import APP_STYLESHEET

    qt_app.setStyleSheet(APP_STYLESHEET)

    config_dir = resolve_config_dir()
    data_dir = resolve_data_dir()
    settings_store = JsonSettingsStore(config_dir / "settings.json")
    secrets = KeyringSecrets()

    needs_setup = settings_store.get("onboarding_complete") != "1"
    if needs_setup and not _run_onboarding(settings_store, secrets):
        sys.exit(0)

    extractor = PdfDocxTextExtractor()
    documents = FilesystemDocumentRepository(data_dir, settings_store, extractor)
    alignment_repo = SqliteAlignmentRepository(data_dir / "alignments.sqlite")
    pdf_renderer = ChromiumPdfRenderer()
    job_fetcher = ChainedJobFetcher()

    create_uc = _build_create_alignment(
        settings_store, secrets, alignment_repo, pdf_renderer, data_dir
    )
    list_uc = ListAlignments(alignment_repo)
    set_docs_uc = SetBaseDocuments(documents)

    deps = MainDeps(
        create_alignment=create_uc,
        list_alignments=list_uc,
        set_base_documents=set_docs_uc,
        documents=documents,
        job_fetcher=job_fetcher,
        alignment_repo=alignment_repo,
    )

    def rebuild_llm() -> CreateAlignment:
        return _build_create_alignment(
            settings_store, secrets, alignment_repo, pdf_renderer, data_dir
        )

    window = MainWindow(
        deps,
        settings_store.get,
        settings_store.set,
        secrets.get,
        secrets.set,
        rebuild_llm,
    )
    window.show()

    tg_token = (secrets.get("telegram_bot_token") or "").strip()
    if tg_token:
        tg_handler = HandleTelegramMessage(job_fetcher, documents, create_uc)
        tg_service = TelegramBotService(tg_token, tg_handler)
        tg_thread = BlockingRunnerThread(tg_service.run_polling_blocking)
        tg_thread.start()
    sys.exit(qt_app.exec())


def _run_onboarding(settings: JsonSettingsStore, secrets: KeyringSecrets) -> bool:
    dlg = QDialog()
    dlg.setWindowTitle("Welcome to AlignAI")
    layout = QVBoxLayout(dlg)
    form = QFormLayout()
    base_url = QLineEdit(settings.get("llm_base_url") or "https://api.openai.com/v1")
    model = QLineEdit(settings.get("llm_model") or "gpt-4o-mini")
    api_key = QLineEdit()
    api_key.setEchoMode(QLineEdit.EchoMode.Password)
    telegram = QLineEdit()
    telegram.setEchoMode(QLineEdit.EchoMode.Password)
    form.addRow("OpenAI-compatible base URL", base_url)
    form.addRow("Model name", model)
    form.addRow("API key", api_key)
    form.addRow("Telegram bot token (optional)", telegram)
    layout.addLayout(form)
    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
    )
    buttons.accepted.connect(dlg.accept)
    buttons.rejected.connect(dlg.reject)
    layout.addWidget(buttons)
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return False
    settings.set("llm_base_url", base_url.text())
    settings.set("llm_model", model.text())
    secrets.set("llm_api_key", api_key.text())
    if telegram.text().strip():
        secrets.set("telegram_bot_token", telegram.text())
    settings.set("onboarding_complete", "1")
    return True


if __name__ == "__main__":
    main()
