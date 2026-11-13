# User README and operator runbook

## Three-step setup
1. Install compatible Python 3.11–3.15.
2. Extract project, open Terminal in folder.
3. Run `./start.sh`, then use the local browser URL shown in Terminal.

## Happy path for a non-developer
1. Enter a recurring research topic (e.g., AI in higher education), choose a publication year and click **Find evidence and build brief**.
2. Check source status and evidence rows. If AI-enabled, review the summary and citations, then edit any unsupported/unclear statements. Open the relevant full texts yourself.
3. Click **Approve reviewed brief**. Download Markdown brief and CSV evidence table. Your approval is logged with UTC timestamp and whether you edited the draft.

## What warnings mean
- **Offline outline (not AI-generated):** no Gemini key. You can test research retrieval and approval, but must enable a key to demonstrate AI synthesis.
- **Offline fallback (AI failed):** model returned an error, invalid JSON or invalid source IDs. Recheck model/key/quota and try again. Never claim this fallback was AI-generated.
- **Source FAILED:** one provider timed out or returned an error. Inspect the other provider and flag potential incompleteness.
- **No valid records:** both sources had no usable items or failed. Try a more common topic, broaden publication year, or check internet.
- **Approval rejected:** edited content is too short; include an overview, actions and citations.

## Operations and monitoring
To rerun regression tests:

```bash
python3 scripts/run_checks.py
```

Review `.data/researchflow.sqlite` for approvals (local only). Use an independent copy/backup when handing off any valuable data. The app does not publish or send email. Never copy API keys into README, GitHub, screenshots, demo video or evaluation logs.

## Reproducibility checklist
- Fresh virtualenv installation works on another laptop.
- Real internet query shows each source succeeded.
- A non-developer can independently review, approve and download.
- No key or API secret is in git history.
- Failure simulation and correction evidence documented.
