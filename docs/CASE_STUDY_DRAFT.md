# Case Study — ResearchFlow AI

**Status: Draft. Fill in independently measured evidence before submitting. Do not present assumptions as interviews or completed field observations.**

## Summary
For an *assumed* weekly research analyst, researching a topic across two academic metadata sources and assembling a brief is repetitive. I developed ResearchFlow AI, a Streamlit-based research intake and reading-brief workflow integrating OpenAlex and Crossref with optional Gemini synthesis, DOI deduplication, validation, approval, export and local audit logging. Preliminary automated synthetic checks test core behavior, but productivity improvements and live integration results remain unmeasured until the protocol is executed.

## User and job to be done
Target user assumption: a junior research/marketing analyst produces one weekly evidence scan and a set of follow-up actions. They want to find relevant recent publications, merge overlapping results, preserve source links and deliver a reviewable summary. **Validation to add:** date, role of interviewee/proxy user, frequency, real quotes (only if genuinely collected), observation notes and data handling permissions.

## Before workflow (to observe and document)
Trigger: recurring topic request or weekly scan. Inputs: topic, desired publication window. Judgments: which sources and citations matter. Tools: manual search across two sites + document editor. Output: sourced research note. Exceptions: duplicates, broken DOIs, incomplete abstracts, unavailable websites, papers behind paywalls. **Add measured manual baseline time and quality here.**

## New workflow and five-day scope
A topic goes through validation → simultaneous conceptual queries to OpenAlex/Crossref (implemented sequentially for clarity) → metadata normalization → DOI/title deduplication → deterministic ranking → optional Gemini JSON brief → source-ID validation → human editing and approval → Markdown/CSV export + SQLite audit entry. Scope deliberately excludes full-text scraping, automated publishing, multi-user auth and paid hosting.

## Architecture and ownership
The two external data APIs are integrated separately, with independent failure handling. The optional AI integration is bounded by a structured JSON contract: summaries/themes/actions/limitations, with source references constrained to retrieved IDs. Human users retain source verification, quality judgment and final approval. See `ARCHITECTURE.md` for contract details.

## Tests, failures and changes
Synthetic unit tests: generate results through `python3 scripts/run_checks.py`, then quote the observed number of passes and the actual generated report. The included mocked failure cases cover a one-source outage, both-source outage, invalid citations and AI-format failure. **Live API reliability, performance, before/after regression and proxy-user feedback are not yet tested or recorded.**

For at least three failures, fill the following:

| Failure | Reproduction | Root cause | Change/fix | Regression outcome |
|---|---|---|---|---|
| One provider inaccessible | Mock source A down; rerun live if an outage occurs | Independent external API failure | Keep surviving provider, show warning | Test 08 unit pass; add live result |
| AI invents nonexistent citation | Supply S999 in mocked AI result | Untrusted generative output | Validate IDs, use labeled fallback | Test 11 unit pass |
| Model gives malformed response | Raise structured-output error in mock | Parsing/schema mismatch | Labeled non-AI fallback | Test 14 unit pass; add live result |

## Baseline versus final — fill with observed facts

| Metric | Manual baseline | ResearchFlow | Method |
|---|---|---|---|
| Median end-to-end time | Not yet measured | Not yet measured | Same user, matched topics, stopwatch incl. review |
| Source citation accuracy | Not yet measured | Not yet measured | Independent source audit |
| Human touches | Not yet measured | Not yet measured | Count interventions incl. approval |
| Completion/reliability | Not yet measured | Not yet measured | Ten-case evaluation |
| API/hosting expense | Not yet measured | Not yet measured | Verify actual service usage |

An unmeasured KPI is not a success claim. To complete the case study, carry out the evaluation in `evaluation/EVALUATION_PLAN.md` and replace these placeholders.

## Limitations
Search corpus and returned abstracts are incomplete, DOI/title dedup may over- or under-merge, and AI may make errors even with citation validation. A sourced reading plan is not a verified systematic literature review. Free tiers have constraints. Adoption by a real user has not been demonstrated until a proxy or intended user completes a hands-off test.

## Two-week follow-up plan
Week 1: observe three independent use attempts; log time, corrections, broken-source incidents and approval quality. Week 2: compare new briefs against manual baseline, review user feedback, add cache/structured rationale and iterate citation/abstract evidence checks. This is a plan, not measured post-deployment adoption.
