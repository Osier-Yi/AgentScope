# -*- coding: utf-8 -*-
"""Tutorial 13: Agent Service — Deploy DataMuse as a production service.

This tutorial demonstrates:
- Using create_app() to build a FastAPI service
- Zero-dep storage via fakeredis (swap to real Redis in production)
- LocalWorkspaceManager with skill_paths to inject T06 skills
- The complete API flow: Credential → Agent → Session → Chat
- SSE streaming communication

Two ways to drive the service:
  - terminal A: python main.py            (this file — starts the service)
  - terminal B: python client.py          (httpx walkthrough of the 5 steps)

Or use the companion Web UI in examples/web_ui.

Prerequisites:
- pip install "agentscope[service]" httpx
- pip install fakeredis            # zero-dep in-memory storage
- DASHSCOPE_API_KEY (or OPENAI_API_KEY) in env
"""
import os
from pathlib import Path

TUTORIAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TUTORIAL_DIR.parent.parent


def _make_inmemory_storage():
    """Build a RedisStorage backed by an in-process fakeredis client.

    Same pattern AgentScope's own RedisStorage unit tests use — no Redis
    server required, no extra StorageBase implementation to maintain.
    """
    try:
        import fakeredis.aioredis
    except ImportError as missing:
        raise ImportError(
            "Tutorial 13 defaults to an in-memory store backed by fakeredis. "
            "Install it with: pip install fakeredis\n"
            "Or edit main.py to use RedisStorage(host=..., port=...).",
        ) from missing

    from agentscope.app import RedisStorage
    from agentscope.app.storage._redis_storage import RedisKeyConfig

    # pylint: disable=protected-access
    # Mirrors the pattern in tests/storage_redis_test.py — we deliberately
    # construct a bare RedisStorage and swap its backing client for fakeredis.
    storage = RedisStorage.__new__(RedisStorage)
    storage._client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    storage._external_pool = None
    storage._owned_pool = None
    storage.key_ttl = None
    storage.key_config = RedisKeyConfig()
    return storage


def create_service():
    """Create the AgentScope service application."""
    import uvicorn
    from fastapi.middleware import Middleware
    from fastapi.middleware.cors import CORSMiddleware

    from agentscope.app import (
        create_app,
        LocalWorkspaceManager,
    )

    basedir = str(TUTORIAL_DIR / "workspaces")

    # Seed every new workspace with T06's report_writer skill so the Agent
    # can produce Markdown reports through a real Skill, not just by hand.
    skill_dirs = [
        str(
            REPO_ROOT / "tutorials" / "06_skills" / "skills" / "report_writer",
        ),
    ]

    app = create_app(
        storage=_make_inmemory_storage(),
        workspace_manager=LocalWorkspaceManager(
            basedir=basedir,
            skill_paths=skill_dirs,
        ),
        extra_middlewares=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
            ),
        ],
        title="DataMuse Service",
        version="1.0.0",
    )

    return app, uvicorn


def print_overview():
    """Print where to go next once the service is running."""
    print(
        """
Tutorial 13: Agent Service
============================================================
Storage : fakeredis (in-memory)        — swap RedisStorage for prod
Skills  : tutorials/06_skills/skills/report_writer injected
Docs    : http://localhost:8000/docs

Drive the service in another terminal:
  python client.py        — Python httpx walkthrough (5 API calls)

Or with curl:
  Step 1  POST /credential/         Register a Credential
  Step 2  POST /agent/              Create an Agent template
  Step 3  POST /sessions/           Create a Session + bind a model
  Step 4  POST /chat/               Stream a reply via SSE
  Step 5  GET  /sessions/{id}/messages?agent_id=...

Or with the official Web UI:
  cd examples/web_ui && pnpm install && pnpm dev
  Setup page: server http://localhost:8000, username demo-user

Press Ctrl+C to stop.
""",
    )


if __name__ == "__main__":
    print_overview()

    if not os.getenv("DASHSCOPE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print(
            "WARNING: neither DASHSCOPE_API_KEY nor OPENAI_API_KEY is set. "
            "The service will start but /chat calls will fail until you "
            "register a working credential.\n",
        )

    try:
        service_app, runner = create_service()
    except ImportError as exc:
        print(f"\nCannot start service: {exc}")
        raise SystemExit(1) from exc

    runner.run(service_app, host="0.0.0.0", port=8000)
