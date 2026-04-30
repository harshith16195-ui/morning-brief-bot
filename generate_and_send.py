#!/usr/bin/env python3
import os
import subprocess
import sys
import time
import anthropic

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BRIEF_PATH = os.path.join(SCRIPT_DIR, "brief_content.html")

SYSTEM_PROMPT = """You are a professional market analyst. Your ONLY output must be a valid HTML document — no preamble, no explanation, no markdown fences. Start your response with <!DOCTYPE html> and end with </html>.

Use web_search to get real-time data (3-4 targeted searches). Then write the HTML brief covering:
- Global Markets (US indices close, DXY, US 10Y yield)
- Gift Nifty Setup (level, implied open)
- FII/DII Flows (provisional cash segment)
- Commodities (Brent, WTI crude, Gold)
- Key News (top 5 items affecting Indian markets)
- Stocks to Watch (5-8 names with catalysts)
- Trade Setup (Nifty + BankNifty support/resistance, day bias)
- Quick Verdict (one paragraph outlook)

Styling: background #0d1117, text #e6edf3, section cards with #161b22 background, green (#3fb950) for positive, red (#f85149) for negative, header in #58a6ff. Keep HTML concise — inline CSS only, no external resources."""


def api_call_with_retry(client, **kwargs):
    for attempt in range(5):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError as e:
            wait = 65 if attempt == 0 else 30 * (attempt + 1)
            print(f"  Rate limit hit, waiting {wait}s before retry {attempt + 1}/5...")
            time.sleep(wait)
    raise RuntimeError("Exceeded retry limit on rate limit errors")


def extract_html(text: str) -> str:
    """Strip any markdown fences or preamble; return just the HTML."""
    import re
    # Pull content from ```html ... ``` fence if present
    m = re.search(r"```(?:html)?\s*(<!DOCTYPE[\s\S]+?)\s*```", text, re.IGNORECASE)
    if m:
        return m.group(1)
    # Otherwise find first < to last >
    start = text.find("<!DOCTYPE")
    if start == -1:
        start = text.find("<html")
    if start != -1:
        return text[start:]
    return text


def generate_brief() -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    tools = [{"type": "web_search_20250305", "name": "web_search"}]

    messages = [
        {
            "role": "user",
            "content": (
                "Generate today's morning market brief for Indian equity traders. "
                "Do 3-4 web searches to get current data, then write the complete HTML document."
            )
        }
    ]

    print("Generating morning market brief with Claude + live web search...")

    while True:
        response = api_call_with_retry(
            client,
            model="claude-haiku-4-5-20251001",
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        for block in response.content:
            if hasattr(block, "type") and block.type == "tool_use":
                query = block.input.get("query", "") if hasattr(block, "input") else ""
                if query:
                    print(f"  Searching: {query}")

        if response.stop_reason in ("end_turn", "max_tokens"):
            if response.stop_reason == "max_tokens":
                print("Warning: max_tokens reached, using partial output.")
            raw = ""
            for block in response.content:
                if hasattr(block, "text"):
                    raw += block.text
            return extract_html(raw)

        elif response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

        else:
            print(f"Unexpected stop reason: {response.stop_reason}", file=sys.stderr)
            sys.exit(1)


def main():
    html = generate_brief()

    with open(BRIEF_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Brief saved to {BRIEF_PATH}")

    send_script = os.path.join(SCRIPT_DIR, "send_brief.py")
    result = subprocess.run(
        [sys.executable, send_script]
    )
    if result.returncode != 0:
        print(f"Email send failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
