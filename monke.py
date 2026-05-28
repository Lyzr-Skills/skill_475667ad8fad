#!/usr/bin/env python3
"""
monke — token-saving text compressor.
Drops articles, filler, pleasantries, hedging.
Short synonyms. Preserves code blocks and technical terms.
"""

import re
import sys
import argparse


# ── Replacement map (order matters: longest phrases first) ──────────────────

REPLACEMENTS = [
    # Pleasantries / openers  (full-phrase first, then fragments)
    (r"\bI\S{0,2} be happy to\b", ""),
    (r"\bI\S{0,2} be glad to\b", ""),
    (r"\bI\S{0,2} be delighted to\b", ""),
    (r"\bI\S{0,2} here to help\b", ""),
    (r"\bhappy to\b", ""),
    (r"\bglad to help\b", ""),
    (r"\bsure[,!]?\s*", ""),
    (r"\bcertainly[,!]?\s*", ""),
    (r"\bof course[,!]?\s*", ""),
    (r"\bgreat question[,!]?\s*", ""),
    (r"\babsolutely[,!]?\s*", ""),
    (r"\bno problem[,!]?\s*", ""),
    (r"\bfeel free to\b", ""),

    # Hedging
    (r"\bit seems (?:like |that )?", ""),
    (r"\bit appears (?:like |that )?", ""),
    (r"\bI think\b", ""),
    (r"\bI believe\b", ""),
    (r"\bI would suggest\b", "suggest"),
    (r"\byou may want to\b", ""),
    (r"\byou might want to\b", ""),
    (r"\byou could consider\b", "consider"),
    (r"\bperhaps\b", ""),
    (r"\bpossibly\b", ""),
    (r"\bprobably\b", ""),
    (r"\bmight be\b", "is"),
    (r"\bshould be able to\b", "can"),

    # Filler adverbs
    (r"\bjust\b", ""),
    (r"\breally\b", ""),
    (r"\bbasically\b", ""),
    (r"\bactually\b", ""),
    (r"\bsimply\b", ""),
    (r"\bessentially\b", ""),
    (r"\bliterally\b", ""),
    (r"\bvery\b", ""),
    (r"\bquite\b", ""),

    # Articles (standalone only — not inside technical terms)
    (r"\bthe\b\s*", ""),
    (r"\ba\b\s*(?=[a-z])", ""),
    (r"\ban\b\s*(?=[aeiou])", ""),

    # Verbose phrases → short synonyms
    (r"\bimplement a solution for\b", "fix"),
    (r"\bimplement(?:ation)? of\b", "use"),
    (r"\butilize\b", "use"),
    (r"\bdemonstrate\b", "show"),
    (r"\bverify\b", "check"),
    (r"\bvalidate\b", "check"),
    (r"\bextensive\b", "big"),
    (r"\bsignificant\b", "big"),
    (r"\bsubstantial\b", "big"),
    (r"\bfunctionality\b", "feature"),
    (r"\bthe following\b", ""),
    (r"\bin order to\b", "to"),
    (r"\bdue to the fact that\b", "because"),
    (r"\bfor the purpose of\b", "for"),
    (r"\bwith respect to\b", "re"),
    (r"\bwith regard to\b", "re"),
    (r"\bit is important to note that\b", ""),
    (r"\bplease note that\b", ""),
    (r"\bit is worth noting that\b", ""),
    (r"\bkeep in mind that\b", ""),
    (r"\bone of the\b", ""),
    (r"\bin the case of\b", "for"),
    (r"\bmake sure to\b\s*", ""),
    (r"\bmake sure\b", "ensure"),
    (r"\bin this case\b", "here"),
    (r"\bat this point\b", "now"),
    (r"\bat this time\b", "now"),
    (r"\bcurrently\b", "now"),
    (r"\bpresently\b", "now"),
]

# Compile with IGNORECASE
COMPILED = [(re.compile(pat, re.IGNORECASE), repl) for pat, repl in REPLACEMENTS]


def extract_code_blocks(text: str):
    """
    Pull out all code blocks (``` ... ```) and replace with placeholders.
    Returns (modified_text, {placeholder: original_block}).
    """
    blocks = {}
    counter = [0]

    def replace_block(m):
        key = f"\x00CODE{counter[0]}\x00"
        blocks[key] = m.group(0)
        counter[0] += 1
        return key

    # Fenced code blocks (``` or ~~~)
    modified = re.sub(r"```[\s\S]*?```|~~~[\s\S]*?~~~", replace_block, text)
    # Inline code `...`
    modified = re.sub(r"`[^`\n]+`", replace_block, modified)
    return modified, blocks


def restore_code_blocks(text: str, blocks: dict) -> str:
    for key, original in blocks.items():
        text = text.replace(key, original)
    return text


def compress(text: str) -> str:
    # 1. Protect code blocks
    text, blocks = extract_code_blocks(text)

    # 2. Apply replacements
    for pattern, replacement in COMPILED:
        text = pattern.sub(replacement, text)

    # 3. Clean up whitespace artifacts
    text = re.sub(r" {2,}", " ", text)          # multiple spaces → single
    text = re.sub(r" ([,\.;:!?])", r"\1", text) # space before punctuation
    text = re.sub(r"\n{3,}", "\n\n", text)      # 3+ newlines → 2
    text = re.sub(r"^\s+", "", text, flags=re.MULTILINE)  # leading spaces per line
    text = text.strip()

    # 4. Restore code blocks
    text = restore_code_blocks(text, blocks)

    return text


def token_count(text: str) -> int:
    """Rough token estimate: whitespace-split words."""
    return len(text.split())


def main():
    parser = argparse.ArgumentParser(
        description="monke: compress AI text to save tokens.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python monke.py --text "Sure! I'd be happy to help you with that issue."
  python monke.py --file response.txt
  echo "Actually, you might want to utilize the following approach." | python monke.py --stdin
        """,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Text string to compress")
    group.add_argument("--file", type=str, help="Path to text file to compress")
    group.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--no-stats", action="store_true", help="Suppress token stats")
    parser.add_argument("--out", type=str, help="Write output to file instead of stdout")

    args = parser.parse_args()

    # ── Load input ───────────────────────────────────────────────────────────
    if args.text:
        original = args.text
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            original = f.read()
    else:  # stdin
        original = sys.stdin.read()

    # ── Compress ─────────────────────────────────────────────────────────────
    compressed = compress(original)

    # ── Stats ────────────────────────────────────────────────────────────────
    orig_tokens = token_count(original)
    comp_tokens = token_count(compressed)
    saved = orig_tokens - comp_tokens
    pct = (saved / orig_tokens * 100) if orig_tokens > 0 else 0

    # ── Output ───────────────────────────────────────────────────────────────
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(compressed)
        if not args.no_stats:
            print(f"[monke] {orig_tokens} → {comp_tokens} tokens | -{saved} ({pct:.1f}% saved) | written to {args.out}")
    else:
        print(compressed)
        if not args.no_stats:
            print(f"\n[monke] {orig_tokens} → {comp_tokens} tokens | -{saved} ({pct:.1f}% saved)")


if __name__ == "__main__":
    main()
