"""ResearchFlow AI Streamlit interface for a non-developer research analyst."""
from __future__ import annotations
import csv
import io
import os
from datetime import date

import streamlit as st
from researchflow.workflow import run_workflow
from researchflow.storage import save_approval, recent_approvals

st.set_page_config(page_title="ResearchFlow AI", page_icon="📚", layout="wide")
st.title("📚 ResearchFlow AI")
st.caption("Source-backed research intake → verified metadata → optional AI brief → human approval → export")

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Gemini API key (optional for outline preview)",
                            value=os.environ.get("GEMINI_API_KEY", ""), type="password",
                            help="Use a free-tier API key. Never put the key in screenshots or commit it to GitHub.")
    st.write("**AI mode:** " + ("available" if api_key else "not configured; offline outline only"))
    st.info("ResearchFlow uses OpenAlex + Crossref public APIs. AI output is never published without human approval.")
    st.caption("Use only non-sensitive or synthetic topics and metadata on a free AI tier.")

with st.form("research_form"):
    topic = st.text_input("Recurring research topic", value="AI in higher education")
    year = st.number_input("Papers published since", min_value=2000,
                            max_value=date.today().year, value=max(2022, date.today().year - 3), step=1)
    submitted = st.form_submit_button("Find evidence and build brief", type="primary")

if submitted:
    try:
        with st.spinner("Checking two source APIs, normalizing evidence, generating a review brief..."):
            result = run_workflow(topic, int(year), api_key=api_key)
            st.session_state["result"] = result
            st.session_state["editable_brief"] = result["markdown"]
            st.session_state["approval_id"] = None
    except Exception as exc:
        st.session_state.pop("result", None)
        st.error(f"Could not complete this run: {str(exc)}")

result = st.session_state.get("result")
if result:
    a, b, c, d = st.columns(4)
    a.metric("Source results", result["source_count"])
    b.metric("Unique records", result["unique_count"])
    c.metric("Duplicates removed", result["duplicates_removed"])
    d.metric("Run time", f"{result['elapsed_seconds']:.2f}s")
    st.caption(f"OpenAlex: {result['source_status'].get('OpenAlex', '?')} | Crossref: {result['source_status'].get('Crossref', '?')} | {result['mode']}")
    for warning in result["warnings"]:
        st.warning(warning)
    st.subheader("1. Review the retrieved sources")
    rows = [{"ID": p["id"], "Title": p["title"], "Year": p["year"], "DOI": p["doi"],
             "Source(s)": ", ".join(p["sources"]), "URL": p["url"]} for p in result["papers"]]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.subheader("2. Edit and approve the brief")
    st.caption("This draft may contain mistakes. Check abstracts and full papers before approving claims.")
    st.text_area("Editable research brief", key="editable_brief", height=380)
    if st.button("Approve reviewed brief", type="primary"):
        if len(st.session_state["editable_brief"].strip()) < 100:
            st.error("The approved brief is too short. Review and restore important citations.")
        else:
            approval_id = save_approval(result, st.session_state["editable_brief"])
            st.session_state["approval_id"] = approval_id
            st.success(f"Saved approval #{approval_id} with timestamp, source counts and edit flag.")
    if st.session_state.get("approval_id"):
        st.download_button("Download approved brief (.md)", data=st.session_state["editable_brief"],
                           file_name="researchflow-approved-brief.md", mime="text/markdown")
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["ID", "Title", "Year", "DOI", "Source(s)", "URL"])
        writer.writeheader()
        writer.writerows(rows)
        st.download_button("Download evidence table (.csv)", data=buf.getvalue(),
                           file_name="researchflow-evidence.csv", mime="text/csv")
    else:
        st.caption("Exports unlock after approval so drafts cannot be confused with final output.")

st.divider()
st.subheader("Audit history")
log = recent_approvals()
if log:
    st.dataframe(log, use_container_width=True, hide_index=True)
else:
    st.caption("No approved briefs yet. Run a query, review the draft, and approve it to create the first record.")
