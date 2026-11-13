# AI collaboration note — disclose and verify

## AI tools and roles
- **ChatGPT (OpenAI):** helped propose the project scope, develop prototype Python/Streamlit code, write synthetic unit tests, structure architecture/runbook/evaluation artifacts, and draft this note. AI-generated code and text are subject to review and correction.
- **Gemini API (Google), when configured:** proposed a cautious source-cited reading brief from OpenAlex/Crossref metadata. This is an **optional runtime dependency**; never claim Gemini was used in live runs unless the app displays `AI-assisted / human review required` and a real request succeeded.
- **Other AI tools:** none documented. Add any actually used; do not invent usage.

## What was delegated versus retained
AI-assisted work: code generation, proposed design and error-handling strategies, draft documentation and test scenarios. **Candidate must personally own:** verifying chosen user and recurring problem, running the app on their Mac, inspecting source API output, understanding/debugging code, configuring their own API key, capturing true baseline timings, recruiting a proxy user, reviewing citations and AI output, documenting rejected corrections, creating demo recording and final submission decisions.

## How to verify generated results
1. Run `python3 scripts/run_checks.py`; inspect actual output rather than relying on this draft's claims.
2. Run two live source queries, confirm both connectors return results and that sample DOIs resolve.
3. Run Gemini in real AI mode (not outline fallback), review source-ID matches and claims.
4. Try failure cases, log observed errors and verify fallbacks.
5. Compare with a timed manual baseline and record all measurements transparently.

## Rejections/manual changes log — candidate to fill
| Date | AI suggestion/result | Why rejected or corrected | Final decision | Evidence |
|---|---|---|---|---|
| [fill] | [fill] | [fill] | [fill] | [test/log] |

## Decisions you should be able to explain at interview
Why these two APIs, why human approval, how DOI dedup works, how source-ID validation helps, what happens when Gemini fails, which evaluation cases are mocked, and why the result cannot be called a full literature review. Keep a personal list of modifications and tests you directly performed.
