"""Observability — Langfuse tracing, evals, prompt management.

Instrumentation stays opt-in (LANGFUSE_ENABLED) so local dev without keys
works out of the box. Never log raw cost values to traces in production;
redact in the trace layer, not in the callers.
"""

from functools import lru_cache

from app.config import settings


@lru_cache
def get_langfuse():
    if not settings.langfuse_enabled or not settings.langfuse_secret_key:
        return None
    from langfuse import Langfuse

    return Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )
