import unittest

from app import fake_model, route_reply


class RoutingTests(unittest.TestCase):
    def test_shipping(self):
        self.assertEqual(
            route_reply("shipping", "  Let’s check your delivery.  "),
            ("staff_draft", "Let’s check your delivery."),
        )

    def test_refund(self):
        self.assertEqual(
            route_reply("refund", fake_model("refund")),
            ("human_review", ""),
        )

    def test_unknown(self):
        self.assertEqual(
            route_reply("unknown", fake_model("unknown")),
            ("human_review", ""),
        )

    def test_empty(self):
        self.assertEqual(route_reply("shipping", "   "), ("human_review", ""))

    def test_non_text(self):
        self.assertEqual(route_reply("shipping", None), ("human_review", ""))
