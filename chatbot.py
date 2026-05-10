"""
chatbot.py: Claude API engine for Vela
  - Loads three plan PDFs once at startup
  - Caches the document corpus via Anthropic prompt caching
  - Maintains per-session conversation history
  - Exposes both blocking and streaming chat interfaces
"""

from __future__ import annotations

import anthropic
from pathlib import Path
from typing import Generator

from config import (
    ANTHROPIC_API_KEY,
    MODEL,
    SYSTEM_PROMPT,
    PDF_PATHS,
)

# ---------------------------------------------------------------------------
# PDF extraction
# ---------------------------------------------------------------------------

def _extract_pdf_text(path: Path) -> str:
    """Return the full text of a PDF, page-joined with blank lines."""
    try:
        import pypdf
    except ImportError as exc:
        raise ImportError("pypdf is required: pip install pypdf") from exc

    if not path.exists():
        raise FileNotFoundError(f"Plan document not found: {path}")

    reader = pypdf.PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(p.strip() for p in pages if p.strip())


def _load_plan_documents() -> str:
    """Load all three plan PDFs and return as a single labelled string."""
    labels = {
        "cigna_global":         "CIGNA GLOBAL — International Health Plan",
        "img_patriot_lite":     "IMG PATRIOT LITE — Travel Medical Insurance",
        "img_patriot_platinum": "IMG PATRIOT PLATINUM — Travel Medical Insurance (Premium)",
    }
    sections: list[str] = []
    for key, path in PDF_PATHS.items():
        text = _extract_pdf_text(path)
        sections.append(f"=== {labels[key]} ===\n\n{text}")
    return "\n\n\n".join(sections)


# ---------------------------------------------------------------------------
# Chatbot
# ---------------------------------------------------------------------------

class VelaChatbot:
    """
    Stateful Claude-powered chatbot for Vela.

    PDF documents are loaded once at __init__ and placed in cached system
    blocks so the large corpus is only billed on the first call per cache TTL
    (5 minutes).  Subsequent calls within that window pay only for the new
    conversation tokens.

    Usage
    -----
    bot = VelaChatbot()
    reply = bot.chat("Hi, I need travel insurance for a trip to France")

    # Streaming (yields str chunks as they arrive)
    for chunk in bot.stream_chat("Do the IMG plans cover dental emergencies?"):
        print(chunk, end="", flush=True)

    bot.reset()   # start a new conversation without reloading PDFs
    """

    def __init__(self) -> None:
        if not ANTHROPIC_API_KEY:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is not set. "
                "Export it before running: set ANTHROPIC_API_KEY=sk-ant-..."
            )

        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.history: list[dict] = []

        plan_text = _load_plan_documents()

        # Two cached system blocks:
        #   1. Vela's identity & guardrails   (~1K tokens, stable)
        #   2. PDF corpus                     (large, stable — the expensive one)
        # Both get ephemeral cache_control so they are billed at cache write
        # price on first call and cache read price (~10% of input) thereafter.
        self._system: list[dict] = [
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": (
                    "PLAN DOCUMENTS\n"
                    "==============\n"
                    "The following are the complete plan documents you are grounded in. "
                    "Answer all coverage questions using only these documents. "
                    "If the answer is not in these documents, say so.\n\n"
                    + plan_text
                ),
                "cache_control": {"type": "ephemeral"},
            },
        ]

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def chat(self, user_message: str) -> str:
        """
        Send a message and return Vela's full reply as a string.
        Blocks until the response is complete.
        """
        self.history.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=1536,
            system=self._system,
            messages=self.history,
            thinking={"type": "adaptive"},
        )

        reply = self._extract_text(response.content)

        # Store only the text in history — thinking blocks are not needed
        # for conversation continuity in a customer-facing chatbot.
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def stream_chat(self, user_message: str) -> Generator[str, None, None]:
        """
        Send a message and yield text chunks as they stream in.
        Builds the full reply into history once streaming is complete.
        Call this in a `for chunk in bot.stream_chat(msg)` loop.
        """
        self.history.append({"role": "user", "content": user_message})

        full_reply = ""

        with self.client.messages.stream(
            model=MODEL,
            max_tokens=1536,
            system=self._system,
            messages=self.history,
            thinking={"type": "adaptive"},
        ) as stream:
            for event in stream:
                # Skip thinking deltas — only surface text to the UI
                if (
                    hasattr(event, "type")
                    and event.type == "content_block_delta"
                    and hasattr(event, "delta")
                    and event.delta.type == "text_delta"
                ):
                    chunk = event.delta.text
                    full_reply += chunk
                    yield chunk

        self.history.append({"role": "assistant", "content": full_reply})

    def reset(self) -> None:
        """Clear conversation history. PDFs stay loaded; cache stays warm."""
        self.history = []

    @property
    def turn_count(self) -> int:
        """Number of complete user→assistant turns so far."""
        return sum(1 for m in self.history if m["role"] == "user")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_text(content: list) -> str:
        """Pull the first text block from a response content list."""
        for block in content:
            if getattr(block, "type", None) == "text":
                return block.text
        return ""


# ---------------------------------------------------------------------------
# Quick smoke-test (python chatbot.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY first.")
        raise SystemExit(1)

    print("Loading plan documents…")
    bot = VelaChatbot()
    print("Ready. Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input or user_input.lower() in {"quit", "exit"}:
            break
        print("Vela: ", end="", flush=True)
        for chunk in bot.stream_chat(user_input):
            print(chunk, end="", flush=True)
        print("\n")
