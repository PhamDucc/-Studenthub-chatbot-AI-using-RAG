"""Checks for the demo API contract and the supplied RAG benchmark."""

import io
import json
import os
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from backend.models import ConversationTurn
from backend.server import Handler, parse_chat_payload, source_summary
from backend.services.chat import answer_question
from backend.services.retrieval import search


BENCHMARK = Path(__file__).resolve().parents[2] / "chatbot" / "tests" / "Smoke_Test_for_RAG.md"


class RetrievalTests(unittest.TestCase):
    def test_expected_source_is_in_top_three_for_supplied_questions(self):
        text = BENCHMARK.read_text(encoding="utf-8")
        cases = re.split(r"(?=^### TC-\d+:)", text, flags=re.M)[1:]
        self.assertEqual(len(cases), 20)
        for section in cases:
            code = re.search(r"TC-\d+", section).group()
            question = re.search(r'\* \*\*Câu hỏi kiểm thử:\*\* \*"(.+?)"\*', section).group(1)
            source_line = re.search(r"\* \*\*Tệp dữ liệu nguồn:\*\* (.+)", section).group(1)
            expected = re.findall(r"`([^`]+\.md)`", source_line)
            with self.subTest(case=code):
                found = {hit.passage.source for hit in search(question, limit=3)}
                self.assertTrue(found.intersection(expected), f"{code}: {found} did not include {expected}")


class ChatTests(unittest.TestCase):
    def test_offline_answer_has_source(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            result = answer_question("Một ngày được tạo mã QR học phí tối đa mấy lần?")
        self.assertEqual(result.mode, "extractive")
        self.assertIn("tối đa 5 lần", result.answer)
        self.assertEqual(result.hits[0].passage.source, "Quy_dinh_ve_hoc_phi.md")

    def test_short_follow_up_uses_previous_question(self):
        history = [ConversationTurn("user", "Một ngày tạo mã QR học phí tối đa mấy lần?")]
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            result = answer_question("Ở đâu?", history)
        self.assertEqual(result.hits[0].passage.source, "Quy_dinh_ve_hoc_phi.md")

    def test_gemini_failure_returns_source_excerpt(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "demo-key"}):
            with patch("backend.services.chat.generate_answer", side_effect=RuntimeError("API unavailable")):
                result = answer_question("Một ngày tạo mã QR học phí tối đa mấy lần?")
        self.assertEqual(result.mode, "extractive")
        self.assertIn("API unavailable", result.warning)
        self.assertTrue(result.hits)


class ApiTests(unittest.TestCase):
    def test_payload_validation(self):
        question, history = parse_chat_payload({
            "question": "  Hỏi về học phí  ",
            "history": [{"role": "user", "content": "  Xin chào  "}],
        })
        self.assertEqual(question, "Hỏi về học phí")
        self.assertEqual(history, [ConversationTurn("user", "Xin chào")])
        for payload in (None, {"question": ""}, {"question": "x", "history": "bad"},
                        {"question": "x", "history": [{"role": "admin", "content": "bad"}]}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                parse_chat_payload(payload)

    def test_post_chat_contract_without_socket(self):
        body = json.dumps({"question": "Một ngày tạo mã QR học phí tối đa mấy lần?"}).encode()
        handler = object.__new__(Handler)
        handler.path = "/chat"
        handler.headers = {"Content-Length": str(len(body))}
        handler.rfile = io.BytesIO(body)
        responses = []
        handler.send_json = lambda status, payload: responses.append((status, payload))
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            handler.do_POST()
        status, payload = responses[0]
        self.assertEqual(status, 200)
        self.assertEqual(payload["mode"], "extractive")
        self.assertTrue(payload["sources"])
        self.assertIn("answer", payload)

    def test_source_summary_has_six_documents(self):
        sources = source_summary()
        self.assertEqual(len(sources), 6)
        self.assertTrue(all(item["passages"] > 0 for item in sources))


if __name__ == "__main__":
    unittest.main()
