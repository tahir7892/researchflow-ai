"""Pure normalization, deduplication and brief formatting operations."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from html import unescape
import json
import re
from typing import Any
from urllib.parse import unquote


@dataclass(frozen=True)
class Paper:
    title: str
    year: int | None
    authors: tuple[str, ...]
    doi: str
    url: str
    abstract: str
    citations: int
    sources: tuple[str, ...]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["authors"] = list(self.authors)
        d["sources"] = list(self.sources)
        return d


def clean_text(value: Any, limit: int = 700) -> str:
    if not isinstance(value, str):
        return ""
    value = re.sub(r"<[^>]*>", " ", value)
    value = unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit]


def normalize_doi(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    value = unquote(value.strip())
    value = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", value, flags=re.I)
    value = re.sub(r"^doi:\s*", "", value, flags=re.I)
    return value.strip().lower() if value.strip().lower().startswith("10.") else ""


def _year(value: Any) -> int | None:
    if isinstance(value, int) and 1600 <= value <= date.today().year + 1:
        return value
    return None


def inverted_abstract(inverted: Any) -> str:
    if not isinstance(inverted, dict):
        return ""
    positions: list[tuple[int, str]] = []
    for token, numbers in inverted.items():
        if not isinstance(token, str) or not isinstance(numbers, list):
            continue
        for n in numbers:
            if isinstance(n, int) and 0 <= n < 3000:
                positions.append((n, token))
    return clean_text(" ".join(word for _, word in sorted(positions)[:150]), 850)


def parse_openalex(data: dict) -> Paper | None:
    title = clean_text(data.get("display_name") or data.get("title"), 250)
    if not title:
        return None
    doi = normalize_doi(data.get("doi"))
    authors = tuple(clean_text(item.get("author", {}).get("display_name"), 90)
                    for item in (data.get("authorships") or [])[:5] if isinstance(item, dict))
    authors = tuple(a for a in authors if a)
    return Paper(title, _year(data.get("publication_year")), authors, doi,
                 ("https://doi.org/" + doi) if doi else str(data.get("id") or ""),
                 inverted_abstract(data.get("abstract_inverted_index")),
                 max(0, int(data.get("cited_by_count") or 0)), ("OpenAlex",))


def parse_crossref(data: dict) -> Paper | None:
    raw = data.get("title") or []
    title = clean_text(raw[0] if isinstance(raw, list) and raw else raw, 250)
    if not title:
        return None
    doi = normalize_doi(data.get("DOI"))
    parts = (data.get("published") or data.get("issued") or {}).get("date-parts") or []
    year = _year(parts[0][0]) if parts and isinstance(parts[0], list) and parts[0] else None
    authors = []
    for person in (data.get("author") or [])[:5]:
        if isinstance(person, dict):
            name = clean_text(" ".join(filter(None, [person.get("given"), person.get("family")])), 90)
            if name:
                authors.append(name)
    return Paper(title, year, tuple(authors), doi,
                 ("https://doi.org/" + doi) if doi else str(data.get("URL") or ""),
                 clean_text(data.get("abstract"), 850),
                 max(0, int(data.get("is-referenced-by-count") or 0)), ("Crossref",))


def deduplicate(papers: list[Paper]) -> list[Paper]:
    results: dict[str, Paper] = {}
    for paper in papers:
        key = "doi:" + paper.doi if paper.doi else (
            "title:" + re.sub(r"[^a-z0-9]", "", paper.title.lower()) + ":" + str(paper.year or ""))
        prev = results.get(key)
        if not prev:
            results[key] = paper
        else:
            results[key] = Paper(
                title=prev.title if len(prev.title) >= len(paper.title) else paper.title,
                year=prev.year or paper.year,
                authors=prev.authors if len(prev.authors) >= len(paper.authors) else paper.authors,
                doi=prev.doi or paper.doi,
                url=prev.url or paper.url,
                abstract=prev.abstract if len(prev.abstract) >= len(paper.abstract) else paper.abstract,
                citations=max(prev.citations, paper.citations),
                sources=tuple(sorted(set(prev.sources + paper.sources))),
            )
    return list(results.values())


def rank(papers: list[Paper], topic: str, limit: int = 10) -> list[dict]:
    tokens = set(re.findall(r"[a-z0-9]{3,}", topic.lower()))
    def score(p: Paper) -> tuple[int, int, int]:
        matches = sum(t in p.title.lower() for t in tokens)
        return matches, p.year or 0, min(p.citations, 1000)
    ranked = sorted(papers, key=score, reverse=True)[:limit]
    return [dict(id=f"S{i}", **p.to_dict()) for i, p in enumerate(ranked, start=1)]


def validate_topic(topic: str) -> str:
    topic = re.sub(r"\s+", " ", topic).strip()
    if not 4 <= len(topic) <= 120:
        raise ValueError("Enter a topic between 4 and 120 characters.")
    return topic


def validate_ai_brief(value: Any, valid_ids: set[str]) -> dict:
    if not isinstance(value, dict):
        raise ValueError("AI response is not an object")
    summary = clean_text(value.get("summary"), 1500)
    if not summary:
        raise ValueError("AI response lacks a summary")
    themes = value.get("themes")
    actions = value.get("actions")
    if not isinstance(themes, list) or not 1 <= len(themes) <= 6:
        raise ValueError("AI response has an invalid themes list")
    if not isinstance(actions, list) or not 1 <= len(actions) <= 8:
        raise ValueError("AI response has an invalid actions list")
    out_themes = []
    for item in themes:
        if not isinstance(item, dict):
            raise ValueError("Theme is invalid")
        refs = item.get("source_ids")
        if not isinstance(refs, list) or not refs or not all(isinstance(r, str) and r in valid_ids for r in refs):
            raise ValueError("AI cited a missing source")
        heading = clean_text(item.get("heading"), 150)
        note = clean_text(item.get("note"), 550)
        if not heading or not note:
            raise ValueError("Theme is missing content")
        out_themes.append({"heading": heading, "note": note, "source_ids": list(dict.fromkeys(refs))})
    out_actions = [clean_text(a, 400) for a in actions if isinstance(a, str) and clean_text(a, 400)]
    if not out_actions:
        raise ValueError("AI response lacks usable actions")
    return {"summary": summary, "themes": out_themes, "actions": out_actions,
            "limitations": clean_text(value.get("limitations"), 1000) or "Evidence is limited to retrieved metadata and available abstracts."}


def outline_brief(topic: str, papers: list[dict]) -> dict:
    """Safe non-AI fallback: NO research claims derived solely from titles."""
    return {"summary": f"Preliminary reading queue for: {topic}. This is an offline outline, not an AI research synthesis. Review source records and abstracts before making evidence claims.",
            "themes": [{"heading": "Candidate sources for review", "note": "Check the complete paper before asserting its findings.",
                        "source_ids": [p["id"] for p in papers[:min(5, len(papers))]]}],
            "actions": ["Open the cited papers and verify relevance and findings.",
                        "Identify gaps and conflicting evidence.",
                        "Edit and approve the brief before distribution."],
            "limitations": "AI not configured or unavailable. Metadata is not proof of research conclusions."}


def render_markdown(topic: str, brief: dict, papers: list[dict], mode: str) -> str:
    lines = [f"# ResearchFlow Brief: {topic}", "", f"Generation mode: **{mode}**", "", "## Overview", "", brief["summary"], "", "## Evidence themes", ""]
    for th in brief["themes"]:
        lines.extend([f"### {th['heading']}", th["note"] + " " + " ".join(f"[{r}]" for r in th["source_ids"]), ""])
    lines.extend(["## Proposed next actions", ""])
    lines.extend([f"- [ ] {act}" for act in brief["actions"]])
    lines.extend(["", "## Limitations", "", brief["limitations"], "", "## Sources (verify primary texts)", ""])
    for p in papers:
        label = f"[{p['id']}] {p['title']} ({p['year'] or 'year unknown'}) — {', '.join(p['sources'])}"
        if p["doi"]:
            label += f" — DOI: {p['doi']}"
        if p["url"].startswith("https://"):
            label += f" — {p['url']}"
        lines.extend([f"- {label}"])
    lines.extend(["", "_Human approval required before external use. Metadata and abstracts can be incomplete._", ""])
    return "\n".join(lines)


def papers_json(papers: list[dict]) -> str:
    return json.dumps(papers, ensure_ascii=False, indent=2)
