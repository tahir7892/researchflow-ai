"""Synthetic tests: these DO NOT prove live integrations or measured time saved."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from researchflow import clients

from researchflow.core import (Paper, deduplicate, normalize_doi, parse_openalex,
                               parse_crossref, rank, validate_topic, validate_ai_brief,
                               render_markdown, outline_brief, inverted_abstract)
from researchflow.workflow import run_workflow
from researchflow.storage import save_approval, recent_approvals


def sample_paper(title="AI tutoring in universities", doi="10.1000/example", source="OpenAlex"):
    return Paper(title, 2025, ("A. Researcher",), doi,
                 "https://doi.org/" + doi if doi else "", "Abstract about student learning.",
                 5, (source,))


class PipelineTests(unittest.TestCase):
    def test_01_openalex_normalization(self):
        raw = {"display_name": "AI tutoring in universities", "publication_year": 2025,
               "doi": "https://doi.org/10.1000/Example", "authorships": [{"author": {"display_name": "A. Researcher"}}],
               "cited_by_count": 8, "abstract_inverted_index": {"Student": [0], "learning": [1]}}
        p = parse_openalex(raw)
        self.assertEqual(p.doi, "10.1000/example")
        self.assertEqual(p.abstract, "Student learning")

    def test_02_crossref_normalization(self):
        raw = {"title": ["AI tutoring in universities"], "published": {"date-parts": [[2025, 4]]},
               "DOI": "10.1000/example", "author": [{"given": "A.", "family": "Researcher"}]}
        p = parse_crossref(raw)
        self.assertEqual(p.year, 2025)
        self.assertEqual(p.authors, ("A. Researcher",))

    def test_03_merge_same_doi(self):
        p1 = sample_paper()
        p2 = sample_paper(source="Crossref")
        combined = deduplicate([p1, p2])
        self.assertEqual(len(combined), 1)
        self.assertEqual(set(combined[0].sources), {"OpenAlex", "Crossref"})

    def test_04_merge_same_title_without_doi(self):
        p1 = sample_paper(doi="")
        p2 = sample_paper(doi="", source="Crossref")
        self.assertEqual(len(deduplicate([p1, p2])), 1)

    def test_05_missing_title_is_dropped(self):
        self.assertIsNone(parse_openalex({"publication_year": 2025}))
        self.assertIsNone(parse_crossref({"title": []}))

    def test_06_reject_invalid_topic(self):
        with self.assertRaises(ValueError):
            validate_topic("AI")

    def test_07_reject_invalid_year(self):
        with self.assertRaises(ValueError):
            run_workflow("AI education", 1995, source_a=lambda *args: [], source_b=lambda *args: [])

    def test_08_partial_source_outage_degrades(self):
        def fail(*args):
            raise ConnectionError("provider unavailable")
        result = run_workflow("AI education", 2024, source_a=fail,
                              source_b=lambda *args: [sample_paper()])
        self.assertEqual(result["unique_count"], 1)
        self.assertEqual(result["source_status"]["OpenAlex"], "FAILED")

    def test_09_both_sources_outage_fails_clearly(self):
        def fail(*args):
            raise ConnectionError("down")
        with self.assertRaisesRegex(RuntimeError, "No valid records"):
            run_workflow("AI education", 2024, source_a=fail, source_b=fail)

    def test_10_no_key_explicitly_not_ai(self):
        result = run_workflow("AI education", 2024,
                              source_a=lambda *args: [sample_paper()], source_b=lambda *args: [])
        self.assertIn("not AI-generated", result["mode"])
        self.assertIn("offline outline", result["markdown"].lower())

    def test_11_ai_invalid_source_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing source"):
            validate_ai_brief({"summary": "Reading queue", "themes": [{"heading": "Theme", "note": "Check", "source_ids": ["S999"]}],
                               "actions": ["Read sources"]}, {"S1"})

    def test_12_bad_ai_structure_rejected(self):
        with self.assertRaisesRegex(ValueError, "themes"):
            validate_ai_brief({"summary": "Summary", "themes": [], "actions": ["Read sources"]}, {"S1"})

    def test_13_valid_ai_path_renders_source_ids(self):
        def ai(_topic, _papers, _key):
            return {"summary": "Preliminary literature review planning summary.",
                    "themes": [{"heading": "Read this first", "note": "Confirm findings in full text", "source_ids": ["S1"]}],
                    "actions": ["Review full paper"], "limitations": "Metadata only"}
        result = run_workflow("AI education", 2024, api_key="fake-key-for-mock-only",
                              source_a=lambda *args: [sample_paper()], source_b=lambda *args: [], generator=ai)
        self.assertIn("AI-assisted", result["mode"])
        self.assertIn("[S1]", result["markdown"])

    def test_14_ai_failure_labeled_fallback(self):
        def ai(*args):
            raise ValueError("unstructured output")
        result = run_workflow("AI education", 2024, api_key="fake-key-for-mock-only",
                              source_a=lambda *args: [sample_paper()], source_b=lambda *args: [], generator=ai)
        self.assertIn("AI failed", result["mode"])
        self.assertTrue(any("synthesis failed" in warning for warning in result["warnings"]))

    def test_15_sqlite_audit_persistence_and_edit_flag(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "audit.sqlite"
            result = run_workflow("AI education", 2024,
                                  source_a=lambda *args: [sample_paper()], source_b=lambda *args: [])
            approval_id = save_approval(result, result["markdown"] + "\nEdited by reviewer", path)
            rows = recent_approvals(path)
            self.assertEqual(approval_id, 1)
            self.assertEqual(rows[0]["reviewed_edit"], 1)

    def test_16_doi_canonicalization(self):
        self.assertEqual(normalize_doi("https://doi.org/10.1234/ABC"), "10.1234/abc")
        self.assertEqual(normalize_doi("https://example.com/not-a-doi"), "")

    def test_17_rank_is_limited(self):
        papers = [sample_paper(f"AI tutoring {i}", f"10.1000/{i}") for i in range(20)]
        ranked = rank(papers, "AI tutoring", limit=10)
        self.assertEqual(len(ranked), 10)
        self.assertEqual(len({p["id"] for p in ranked}), 10)

    def test_18_inverted_abstract_order(self):
        self.assertEqual(inverted_abstract({"world": [1], "Hello": [0]}), "Hello world")

    def test_19_openalex_http_connector_contract(self):
        fixture = {"results": [{"display_name": "AI tutoring in universities", "publication_year": 2025,
                                "doi": "https://doi.org/10.1000/example"}]}
        with patch.object(clients, "request_json", return_value=fixture) as call:
            papers = clients.fetch_openalex("AI tutoring", 2024, 10)
        self.assertEqual(len(papers), 1)
        self.assertIn("api.openalex.org/works?", call.call_args.args[0])
        self.assertIn("search=AI+tutoring", call.call_args.args[0])

    def test_20_crossref_http_connector_contract(self):
        fixture = {"message": {"items": [{"title": ["AI tutoring in universities"],
                                           "DOI": "10.1000/example", "published": {"date-parts": [[2025]]}}]}}
        with patch.object(clients, "request_json", return_value=fixture) as call:
            papers = clients.fetch_crossref("AI tutoring", 2024, 10)
        self.assertEqual(len(papers), 1)
        self.assertIn("api.crossref.org/works?", call.call_args.args[0])
        self.assertIn("from-pub-date", call.call_args.args[0])

    def test_21_gemini_http_json_contract(self):
        content = {"summary": "Preliminary reading queue for AI research.",
                   "themes": [{"heading": "Topic", "note": "Verify full text", "source_ids": ["S1"]}],
                   "actions": ["Read source one"], "limitations": "Metadata only"}
        import json
        fixture = {"candidates": [{"content": {"parts": [{"text": json.dumps(content)}]}}]}
        paper = {"id": "S1", **sample_paper().to_dict()}
        with patch.object(clients, "request_json", return_value=fixture) as call:
            brief = clients.gemini_brief("AI research", [paper], "example-only-key")
        self.assertEqual(brief["themes"][0]["source_ids"], ["S1"])
        self.assertIn("generativelanguage.googleapis.com", call.call_args.args[0])
        self.assertEqual(call.call_args.kwargs["headers"]["x-goog-api-key"], "example-only-key")


if __name__ == "__main__":
    unittest.main()
