"""Workflow orchestration with independently failing sources and safe fallback."""
from __future__ import annotations

import time
from datetime import date
from .core import deduplicate, rank, validate_topic, outline_brief, render_markdown
from .clients import fetch_openalex, fetch_crossref, gemini_brief


def run_workflow(topic: str, since_year: int, api_key: str = "", *, source_a=fetch_openalex,
                 source_b=fetch_crossref, generator=gemini_brief) -> dict:
    started = time.perf_counter()
    topic = validate_topic(topic)
    if not (2000 <= since_year <= date.today().year):
        raise ValueError("Choose a publication year between 2000 and the current year.")
    all_papers = []
    warnings = []
    source_status = {}
    for name, fetcher in (("OpenAlex", source_a), ("Crossref", source_b)):
        try:
            found = fetcher(topic, since_year, 12)
            all_papers.extend(found)
            source_status[name] = f"OK: {len(found)} records"
        except Exception as exc:
            # no private information from exception bodies; only type and a short user-safe message
            source_status[name] = "FAILED"
            warnings.append(f"{name}: {type(exc).__name__}. Retry later or check connectivity.")
    if not all_papers:
        raise RuntimeError("No valid records retrieved from either source. Check network, topic, or date range.")
    unique = deduplicate(all_papers)
    papers = rank(unique, topic, 10)
    mode = "AI-assisted / human review required"
    if not api_key.strip():
        mode = "Offline outline (not AI-generated)"
        brief = outline_brief(topic, papers)
        warnings.append("No Gemini key supplied. Only an offline outline was produced; AI functionality has not run.")
    else:
        try:
            brief = generator(topic, papers, api_key)
        except Exception as exc:
            mode = "Offline fallback (AI failed)"
            brief = outline_brief(topic, papers)
            warnings.append(f"Gemini synthesis failed ({type(exc).__name__}); switched to a clearly labeled outline.")
    markdown = render_markdown(topic, brief, papers, mode)
    return {"topic": topic, "since_year": since_year, "source_status": source_status,
            "source_count": len(all_papers), "unique_count": len(unique), "papers": papers,
            "duplicates_removed": len(all_papers) - len(unique), "mode": mode,
            "warnings": warnings, "markdown": markdown, "elapsed_seconds": round(time.perf_counter() - started, 3)}
