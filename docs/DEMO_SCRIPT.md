# Five-minute demo storyboard

**Recording:** Use macOS built-in screen recording: press Shift-Command-5, select record screen/window, ensure API key/password is not visible. Record in one take if possible. Do not show fabricated data as real, and do not claim results not measured.

**0:00–0:45 — Problem and baseline.** Explain the target analyst, weekly task, manual workflow and the personally collected timing/quality baseline. Say explicitly if the target is a proxy or synthetic user.

**0:45–1:15 — Architecture.** Point at `docs/ARCHITECTURE.md`: two distinct research data integrations, deduplication, bounded Gemini, approval and SQLite audit.

**1:15–3:00 — Real working path.** Open Streamlit. Show Gemini key already configured but hidden, enter a topic, run it. Confirm status says AI-assisted and both sources show OK. Inspect selected records, their DOI links and `[S1]` etc. Correct one draft line and click Approve. Download approved Markdown and CSV.

**3:00–3:45 — Failure handling.** Run `python3 scripts/run_checks.py` in Terminal and show observed results; explain that the tests simulate outages and invalid references. If available, demonstrate a live failure (e.g. missing Gemini key) and visible non-AI outline. Never conflate mocked and live results.

**3:45–4:35 — Measured evaluation.** Open completed `evaluation/baseline_and_results_template.csv` and show actual before/after timings, citation quality and manual intervention; state sample size and important remaining failures. If unmeasured, say that openly.

**4:35–5:00 — Handoff and limitation.** Show `README.md` and runbook. Say the most important limitation: metadata-only briefs require human full-text verification. Show next iteration plan.

**Pre-recording checklist:** actual app starts on your Mac, source URLs resolve, Gemini real mode works, no key in recording, one approved export available, test output saved, accurate evaluation sheet completed, and proxy-user notes captured if claimed.
