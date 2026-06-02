#!/usr/bin/env python
"""
Build a draft glossary from cleaned paper text and chunk manifest.

This script is intentionally heuristic: it extracts candidate technical terms,
acronyms, and section-specific phrases, then writes a review-friendly JSON file.
The result is a glossary draft for manual curation before translation.

Example:
    python 03_glossary.py \
        --input work/clean/generative_ai_labor_demand.clean.md \
        --manifest work/chunks/generative_ai_labor_demand/manifest.json \
        --output work/meta/generative_ai_labor_demand.glossary.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "into",
    "is",
    "less",
    "more",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "their",
    "this",
    "through",
    "to",
    "use",
    "using",
    "we",
    "with",
}

SEED_TERMS = [
    "generative AI",
    "large language model",
    "LLM",
    "job postings",
    "labor demand",
    "job ladder",
    "hiring reallocation",
    "job redesign",
    "posting-level exposure",
    "occupation-level exposure",
    "task content",
    "Oaxaca-Blinder decomposition",
    "Kitagawa decomposition",
    "Lightcast",
    "O*NET",
    "NAICS",
    "ChatGPT",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Clean markdown input.")
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Optional chunk manifest to add section-level occurrence context.",
    )
    parser.add_argument("--output", required=True, type=Path, help="Glossary JSON output.")
    parser.add_argument(
        "--top-n",
        type=int,
        default=80,
        help="Maximum number of candidate entries to keep.",
    )
    return parser.parse_args()


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def iter_candidate_phrases(text: str) -> Iterable[str]:
    acronym_re = re.compile(r"\b(?:[A-Z]{2,}(?:s)?|O\*NET|U\.S\.|GPT-\d+(?:\.\d+)?)\b")
    hyphen_phrase_re = re.compile(r"\b[A-Za-z]+(?:-[A-Za-z]+){1,4}\b")
    noun_phrase_re = re.compile(
        r"\b(?:[A-Za-z][A-Za-z*.-]*\s+){1,4}(?:exposure|demand|market|pipeline|posting|postings|"
        r"decomposition|reallocation|redesign|taxonomy|occupation|occupations|task|tasks|seniority|"
        r"industry|industries|diffusion|framework|measure|measures|dataset|data|tool|tools)\b",
        re.IGNORECASE,
    )

    for match in acronym_re.finditer(text):
        yield match.group(0)
    for match in hyphen_phrase_re.finditer(text):
        yield match.group(0)
    for match in noun_phrase_re.finditer(text):
        yield match.group(0)
    for seed in SEED_TERMS:
        yield seed


def canonicalize(term: str) -> str:
    term = term.strip(" .,:;()[]{}")
    term = re.sub(r"\s+", " ", term)
    return term


def is_good_term(term: str) -> bool:
    if len(term) < 3:
        return False
    if term.lower() in STOPWORDS:
        return False
    if term.isdigit():
        return False
    words = re.split(r"\s+", term)
    if all(word.lower() in STOPWORDS for word in words):
        return False
    return True


def find_examples(text: str, term: str, limit: int = 2) -> List[str]:
    snippets: List[str] = []
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    for match in pattern.finditer(text):
        start = max(0, match.start() - 60)
        end = min(len(text), match.end() + 100)
        snippet = text[start:end].replace("\n", " ")
        snippet = re.sub(r"\s+", " ", snippet).strip()
        snippets.append(snippet)
        if len(snippets) >= limit:
            break
    return snippets


def load_manifest_sections(manifest_path: Path | None) -> Dict[str, List[str]]:
    if manifest_path is None or not manifest_path.exists():
        return {}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    section_map: Dict[str, List[str]] = defaultdict(list)
    for item in data.get("chunks", []):
        chunk_path = Path(item["source_file"])
        section_map[item["title"]].append(str(chunk_path))
    return section_map


def build_glossary(text: str, top_n: int) -> List[Dict[str, object]]:
    counter: Counter[str] = Counter()
    for raw_term in iter_candidate_phrases(text):
        term = canonicalize(raw_term)
        if not is_good_term(term):
            continue
        counter[term] += 1

    scored_terms: List[Tuple[str, int]] = []
    for term, freq in counter.items():
        bonus = 0
        if term in SEED_TERMS:
            bonus += 4
        if any(ch.isupper() for ch in term):
            bonus += 1
        if "-" in term:
            bonus += 1
        scored_terms.append((term, freq + bonus))

    scored_terms.sort(key=lambda item: (-item[1], item[0].lower()))
    chosen = scored_terms[:top_n]

    glossary = []
    for rank, (term, score) in enumerate(chosen, start=1):
        glossary.append(
            {
                "rank": rank,
                "source_term": term,
                "translation": "",
                "status": "draft",
                "score": score,
                "examples": find_examples(text, term),
                "notes": "",
            }
        )
    return glossary


def main() -> None:
    args = parse_args()
    text = normalize_text(args.input.read_text(encoding="utf-8"))
    section_map = load_manifest_sections(args.manifest)
    glossary = build_glossary(text, top_n=args.top_n)

    payload = {
        "version": 1,
        "source_file": str(args.input),
        "manifest_file": str(args.manifest) if args.manifest else None,
        "section_count": len(section_map),
        "entries": glossary,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Glossary draft written to: {args.output}")
    print(f"Draft entries: {len(glossary)}")


if __name__ == "__main__":
    main()
