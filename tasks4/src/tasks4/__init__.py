from __future__ import annotations
import os, sys, argparse, textwrap
from typing import Iterable, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

MODEL = "gpt-5.1-mini"

SYSTEM_PROMPT = (
    "You are a terse summarizer. For each task description, return a concise, "
    "actionable 3–7 word phrase (no ending punctuation)."
)

SAMPLES: List[str] = [
    ("For my CSC299 portfolio checkpoint, I need to collect links to my GitHub repos, "
     "write a 150-word summary of my PKMS CLI progress, and include 2 screenshots "
     "demonstrating add/list/search. I also have to push a README with setup steps."),
    ("Plan the final study sprint for data structures: build a daily schedule, "
     "write 10 practice problems on stacks/queues/recursion, and take two timed ")
]

def summarize_many(paragraphs: Iterable[str]) -> List[str]:
    """Send each paragraph independently to the OpenAI Chat Completions API and return short, phrase-length summaries."""
    client = OpenAI()  # uses OPENAI_API_KEY from environment
    out: List[str] = []
    for text in paragraphs:
        text = text.strip()
        if not text:
            out.append("(empty paragraph)")
            continue
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
            max_tokens=24,
        )
        out.append((resp.choices[0].message.content or "").strip())
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tasks4",
        description="Summarize paragraph-length task descriptions into short phrases (ChatGPT API demo).",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument("--file", "-f", metavar="PATH", help="Read paragraph descriptions from a text file.")
    p.add_argument("--stdin", action="store_true", help="Read paragraph descriptions from STDIN.")
    p.add_argument("--samples", action="store_true", help="Use built-in sample paragraphs (default).")
    return p


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ No OpenAI API key found. Please set it in your .env file or environment.")
        print("   Example (PowerShell): $env:OPENAI_API_KEY = 'sk-...'")
        return 2
    else:
        print("✅ OpenAI API key loaded successfully.\n")

    args = build_parser().parse_args(argv)

    paragraphs: List[str] = []
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            paragraphs = [p.strip() for p in f.read().split("\n\n") if p.strip()]
    elif args.stdin:
        raw = sys.stdin.read()
        paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]
    else:
        paragraphs = SAMPLES

    if not paragraphs:
        print("No paragraphs provided.")
        return 1

    print("🧠 tasks4 — Chat Summarizer\n")
    summaries = summarize_many(paragraphs)

    for i, (src, summ) in enumerate(zip(paragraphs, summaries), start=1):
        print(f"— Task {i} —")
        print(textwrap.shorten(src, width=120, placeholder='…'))
        print(f"Summary: {summ}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


