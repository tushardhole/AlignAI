# Changelog

## 0.1.0 (2026-05-03)


### Features

* add delete button for past alignments in home page table ([94396a8](https://github.com/tushardhole/AlignAI/commit/94396a80e7577fe0228b4a1c8ce3bc6ab0fad21c))
* add delete button for past alignments in home page table ([7baedc5](https://github.com/tushardhole/AlignAI/commit/7baedc5f14edcd51d86fd7da47eab6e59b83b48e))
* add domain models, Protocol ports, and unit tests ([9d58082](https://github.com/tushardhole/AlignAI/commit/9d5808224e070d1ccd180d20f8593731e627a10a))
* add refresh button to home page ([06e029b](https://github.com/tushardhole/AlignAI/commit/06e029bd756156ab2fbb9700ca91f7a2bdea5164))
* add refresh button to home page ([46cf214](https://github.com/tushardhole/AlignAI/commit/46cf214d80724e87f322adf51b61d5ba12c2e2fe))
* add ResumeSection/ParsedResume types and ResumeParser port ([f46cfff](https://github.com/tushardhole/AlignAI/commit/f46cfff3dc5930e0d1a33d031fcb005a6f77b126))
* add ResumeSection/ParsedResume types and ResumeParser port ([e33c791](https://github.com/tushardhole/AlignAI/commit/e33c791df1c606a7fff92ccc0f6bb1264d292d81))
* **agents:** AlignAi runner, chunked resume alignment, structured outputs ([e17beb5](https://github.com/tushardhole/AlignAI/commit/e17beb5e9cfe547e0955445eb4d1761228a888ab))
* **agents:** AlignAi runner, chunked resume alignment, structured outputs ([ec2c7c6](https://github.com/tushardhole/AlignAI/commit/ec2c7c6006e4f4666475a653671648700ee23394))
* **application:** use cases for alignment, listings, credentials, Telegram ([ca769f1](https://github.com/tushardhole/AlignAI/commit/ca769f1cb50b5df51fb32ccff96329386913c7cd))
* **domain:** align MatchLabel set and refine preflight missing-tests gate ([2cb1c8a](https://github.com/tushardhole/AlignAI/commit/2cb1c8abd664ea5845181014dcbf1d9c732adf02))
* **domain:** MatchLabel alignment and preflight missing-tests gate ([f4f51fb](https://github.com/tushardhole/AlignAI/commit/f4f51fbc0286a7c7c97e1ff44c4e84d7aa02976e))
* **infra:** adapters for fetch, storage, PDF, LLM, Telegram ([e3bea7b](https://github.com/tushardhole/AlignAI/commit/e3bea7be27071c71dcfc3ccae4533660e7c05e72))
* **infra:** adapters for paths, settings, fetch, SQLite, PDF, LLM, Telegram ([9baddb2](https://github.com/tushardhole/AlignAI/commit/9baddb2d78b2a6c78ddfd8143eb4db98f66df847))
* UI overhaul, bug fixes, and settings hot-reload ([ab91d25](https://github.com/tushardhole/AlignAI/commit/ab91d259818f5f243f45e7e4b5372801592b1efa))
* UI overhaul, bug fixes, and settings hot-reload ([9d4bb3e](https://github.com/tushardhole/AlignAI/commit/9d4bb3ee1f5b7aaae5812047f9a108471adf3d09))
* **ui:** PySide6 shell, async workers, main entrypoint and Telegram thread ([2c4f0e3](https://github.com/tushardhole/AlignAI/commit/2c4f0e3eceb8458e80a924f096d21474a3d1b6a0))
* **ui:** PySide6 shell, onboarding path, Telegram worker thread ([642e4fd](https://github.com/tushardhole/AlignAI/commit/642e4fd0ab541ab717641616d329876b8468cbe5))


### Bug Fixes

* add missing stubs and mypy overrides for pre-commit hook ([276fa2f](https://github.com/tushardhole/AlignAI/commit/276fa2f0ea6514361cc3f710ed79c1dac161096e))
* always infer match label from score, never store label ([6b79b81](https://github.com/tushardhole/AlignAI/commit/6b79b81f5e20e412dccef9d437937d859ef653aa))
* always infer match label from score, never store label ([6e59193](https://github.com/tushardhole/AlignAI/commit/6e5919358dad479133ba518d143a63bdcbe0ded2))
* apply Fusion style + stylesheet on QApplication for macOS compatibility ([d4a1b5c](https://github.com/tushardhole/AlignAI/commit/d4a1b5cbe9f797a2877786303246ec08308ada99))
* **ci:** ruff TCH ignore, coverage gate domain+application, telegram handler Any ([a5e98af](https://github.com/tushardhole/AlignAI/commit/a5e98af37edfc064fec7a37440b6693d8f4bc9fe))
* delete button font color and Settings button text clipping ([8f18cfe](https://github.com/tushardhole/AlignAI/commit/8f18cfe46b327086a8915944f462f4085e3e2a3e))
* delete button table layout - adjust column width and row height ([ef89325](https://github.com/tushardhole/AlignAI/commit/ef8932513bf484cc03909ef49e8bec91e90e558d))
* format lambda expression on single line ([a68b705](https://github.com/tushardhole/AlignAI/commit/a68b705c7716f3c1dae81e9f8d9e31c3fb6f1e61))
* increase button padding to prevent text clipping ([92ef678](https://github.com/tushardhole/AlignAI/commit/92ef6780303b1d3add5d0037648279dbace89a8a))
* increase refresh button size to prevent icon clipping ([07b63a3](https://github.com/tushardhole/AlignAI/commit/07b63a315683485ff163f848698bedea81f20129))
* increase Settings button width and padding to prevent text clipping ([a458879](https://github.com/tushardhole/AlignAI/commit/a458879f7087db949905a753f8b43ea4318abf84))
* make refresh button visible with label text ([e970844](https://github.com/tushardhole/AlignAI/commit/e9708449b9893ecc640ba30490b62a95f3fc6d4e))
* polish delete button UI and enhance overall app styling ([cd8d0e0](https://github.com/tushardhole/AlignAI/commit/cd8d0e0af28be6e40fbbee6bda267f7fe45f9936))
* properly type alignment_repo in MainDeps for mypy ([bd777b8](https://github.com/tushardhole/AlignAI/commit/bd777b8aefec6580a4a52ad2c2b5914d396cbbd4))
* remove unused type:ignore comment from parsed_resume_fields ([4fe19cb](https://github.com/tushardhole/AlignAI/commit/4fe19cb6ff00c337478293fc39d32637d0a22f86))
* robust LLM JSON coercion and dead code removal ([b97ce90](https://github.com/tushardhole/AlignAI/commit/b97ce900b4dcbc98fa9adddf8db9237c86474a38))
* robust LLM JSON coercion and dead code removal ([0804c61](https://github.com/tushardhole/AlignAI/commit/0804c61ea3264090e0e64fb999abbe21ae68c623))
* ruff formatting and CodeQL URL substring sanitization ([4ddac5f](https://github.com/tushardhole/AlignAI/commit/4ddac5fb138034a42978e36cc1ee3fd0a01f125e))
* ruff import sorting and en-dash lint violations ([6fe57d1](https://github.com/tushardhole/AlignAI/commit/6fe57d106a68cac1ab53eaf9499126bd53ec081f))
* satisfy ruff on package init, models, and ports ([855f308](https://github.com/tushardhole/AlignAI/commit/855f308a7cff1f2b78776ad598509dacd21e8912))
* sort imports and add noqa for intentional multiply sign ([1e00eb0](https://github.com/tushardhole/AlignAI/commit/1e00eb0341d8a408613221d65a202d558f95d349))
* style refresh button exactly like delete button ([10ce8cf](https://github.com/tushardhole/AlignAI/commit/10ce8cf47610055ba50dacda3fabacde8d8042b1))
* style tooltip to match secondary button design ([7e30e1e](https://github.com/tushardhole/AlignAI/commit/7e30e1e6c3f171c4acebaea51486ba0429fd8a88))
* unblock CI lint, preflight import-linter, and coverage gate ([20c7842](https://github.com/tushardhole/AlignAI/commit/20c784216af305d5eef2e902a298618fb238d65b))
* use setuptools.build_meta for editable installs ([bb5867b](https://github.com/tushardhole/AlignAI/commit/bb5867bffbb97a062737273ab74a44b5f09c68e0))


### Documentation

* architecture guides, packaging, presence proxy stub; CI preflight ([29f829a](https://github.com/tushardhole/AlignAI/commit/29f829a6d3812871e648020edc742d1c2dc3c704))
* architecture, usage, AI engineering, releasing ([b42fa08](https://github.com/tushardhole/AlignAI/commit/b42fa0898aecb12d017660ba55d54229c9a7688c))
* fix markdownlint violations in CLAUDE.md and README.md ([4369444](https://github.com/tushardhole/AlignAI/commit/4369444ff471ddaabf2426772f5a90378d3e1cc1))
* wrap Markdown to 80 cols for markdownlint MD013 ([adb63e9](https://github.com/tushardhole/AlignAI/commit/adb63e923b178554a23c5741528f6eac5ef1ac6c))
