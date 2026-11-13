# ResearchFlow AI

> **Status:** Runnable local prototype. 18+ automated synthetic checks passing when last generated. Live API calls, user interview, full baseline measurement and end-to-end Gemini behavior must be verified on the evaluator's machine; no savings are claimed yet.

## What it does
A research analyst enters a topic and publication-year cutoff. ResearchFlow queries **OpenAlex** and **Crossref** (two distinct real public data sources), normalizes results, deduplicates by DOI/title, selects up to ten records, and optionally asks **Gemini** to draft an evidence-aware *reading and action brief*. The analyst edits the draft and clicks **Approve**; the app persists a local SQLite audit entry and unlocks Markdown and CSV exports. Source IDs cited by the AI are checked against the retrieved evidence. When AI is unconfigured/unavailable, a visibly labeled *non-AI outline* is generated instead, and no fabricated claims are supplied.

This is **not** a replacement for reading or verifying scientific papers; metadata and abstracts don't justify conclusive research claims.

## Intended user / authenticity
The initial persona is an **assumed** weekly research or marketing analyst. The workflow's existence and pain must be checked through a real or proxy user; see `evaluation/EVALUATION_PLAN.md`. Synthetic tests are not claimed to be field research.

## Run on an Intel Mac with macOS Ventura

1. **Install Python 3.11** from <https://www.python.org/downloads/> if you don't already have a supported version. Confirm `python3 --version` is 3.11–3.15. Python 3.11 is the conservative choice on your Intel Mac. Free tools only.
2. Extract this ZIP. Open **Terminal**, type `cd ` (with a trailing space), drag the extracted **researchflow-ai** folder from Finder into Terminal, and press Return.
3. Run:

```bash
./start.sh
```

This creates a virtual environment, installs Streamlit, and launches the local UI at **http://localhost:8501** (the terminal shows the exact URL). An internet connection is required for the live source APIs. Mac developer-command-line tools may be requested if Python dependencies need compiling.

**Alternative manual setup:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Free Gemini key (AI mode)

1. Get an API key at <https://aistudio.google.com/apikey> if you are eligible for the free tier.
2. Paste the key into the **Gemini API key** sidebar password box. It is held only in that Streamlit session and is **never stored in SQLite**. Do not show it in the demo recording.
3. Choose a topic like `AI in higher education`, set papers since 2023, and click **Find evidence and build brief**.
4. Confirm the status line says **AI-assisted / human review required**. If it says **Offline outline**, AI did **not** run successfully. Fix API key/model/limits before claiming an AI demo.
5. Review evidence links, edit the generated draft, click **Approve**, then download Markdown and CSV.

Optional environment settings: `GEMINI_API_KEY`, `GEMINI_MODEL` (defaults to `gemini-3.5-flash-lite`), `OPENALEX_API_KEY`, `CONTACT_EMAIL` (Crossref polite pool). Set with `export VARIABLE=value` before running. `.env.example` describes the options; the app intentionally does not auto-read `.env`. Do not commit secrets.

### Model access caveat
Gemini model names, regional/free quotas, and API access may change; consult <https://ai.google.dev/gemini-api/docs/models> and <https://ai.google.dev/gemini-api/docs/pricing>. Some OpenAlex requests have usage budgets, even when anonymous access is currently offered. Stay within free-tier limits and check billing. Free-tier AI content may be used for product improvement; use non-sensitive research topics only.

## How to run real checks

```bash
python3 scripts/run_checks.py
```

The command runs deterministic **synthetic tests**, not live integration calls, and writes `evaluation/observed_unit_tests.json`. Then manually run two real topics via the UI (verify both source statuses show OK), run at least 8–12 scenarios from `evaluation/test_cases.csv`, fill `evaluation/baseline_and_results_template.csv`, and invite a proxy user to attempt the export independently.

## Project map

```text
app.py                             Streamlit interface, approval and downloads
researchflow/core.py               Normalization, DOI dedup, ranked source records, validation
researchflow/clients.py            Real OpenAlex / Crossref / Gemini HTTP connectors
researchflow/workflow.py           End-to-end orchestration and graceful fallback
researchflow/storage.py            SQLite human-approval audit trail
tests/test_core.py                 Synthetic and mocked regression tests
scripts/run_checks.py              Actual observed unit test report generator
evaluation/*                      Test plans, 10 cases, baseline sheet, observed unit results
docs/ARCHITECTURE.md                System/data contracts, risks and design tradeoffs
docs/USER_RUNBOOK.md                User instructions and failure handling
docs/CASE_STUDY_DRAFT.md            Case study to finalize with measured evidence
docs/AI_COLLABORATION_NOTE.md       AI use and what you must verify/own
docs/DEMO_SCRIPT.md                 Five-minute walkthrough storyboard
docs/SUBMISSION_CHECKLIST.md       Five deliverables checklist
```

## Error recovery
- One research API unavailable: use the other and show warning; source status is visible.
- Both unavailable or empty: fail clearly instead of generating fictional sources.
- Gemini timeout/bad JSON/fabricated citation: clearly labeled non-AI fallback; check key/quota and rerun.
- Approval must be manually clicked; it is stored in local `.data/researchflow.sqlite`, which is ignored by Git.

## Known limitations
- Results are API metadata, not extracted full-text paper contents. AI draft is a reading plan, not an evidence-based clinical/business conclusion.
- Some citations may lack DOI or abstract. No-paywall crawling and no PDF ingestion.
- The app is a **local single-user** prototype, not a hosted multi-tenant service. No authentication, backups, or external publishing.
- API response quality, network access and Gemini availability must be verified in a live run.
- Benchmarks must include human review time; no measured improvement asserted in this starter package.

## License & privacy
The code in this bundle is supplied for the assessment prototype and can be adapted. Review any third-party API data and use policies before production use. Don't upload customer secrets or sensitive personal data to a free AI tier.
