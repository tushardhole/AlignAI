# Telegram presence proxy (optional)

This directory holds a **stub** design for an optional cloud-hosted companion
that keeps your Telegram users informed when the AlignAI desktop app is not
polling.

## Problem

Telegram only delivers updates while a bot is actively long-polling (or using a
webhook). If your desktop is off, users get no reply until the next time
AlignAI starts.

## MVP behavior (no proxy)

When AlignAI restarts, queued updates are processed and messages may be prefixed
with an offline notice (see application handler).

## Optional architecture (not shipped)

1. A tiny always-on HTTP endpoint (e.g. Cloudflare Worker, Fly.io, Railway)
   receives Telegram webhooks.
2. The desktop app pings a “heartbeat” URL every few minutes while running.
3. If the heartbeat is stale, the worker auto-replies: “Please start AlignAI on
   your desktop.”
4. When the desktop returns, the worker forwards traffic or instructs the user
   to retry.

Implement this only if you need instant routing instead of
backlog-on-next-launch.

## Stub entrypoint

`main.py` is a placeholder with logging only — **no runtime dependency** for
the desktop MVP.
