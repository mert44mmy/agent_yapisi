import unittest

from core.risk_pipeline import (
    RiskPipelineOrchestrator,
    RiskPipelineState,
    DeterministicRiskAgent,
    load_scenarios,
)


class TestRiskPipeline(unittest.TestCase):
    def test_pipeline_generates_risk_decision(self):
        state = RiskPipelineState(
            user_request=(
                "Applicant income 35000, monthly debt 1200, no prior fraud, "
                "employment 2 years, loan amount 5000"
            )
        )

        agents = [
            DeterministicRiskAgent("financial"),
            DeterministicRiskAgent("fraud"),
            DeterministicRiskAgent("credit"),
        ]

        pipeline = RiskPipelineOrchestrator(agents)
        final_state = pipeline.run(state)

        self.assertIn("decision", final_state.risk_decision)
        self.assertIn("status", final_state.policy_result)
        self.assertIn("action", final_state.authorized_action)
        self.assertIn(final_state.policy_result["status"], {"LOW_RISK", "MANUAL_REVIEW", "HIGH_RISK"})

    def test_dataset_for_scenarios_is_loaded(self):
        scenarios = load_scenarios("veri_seti.json")
        self.assertEqual(len(scenarios), 4)
        self.assertIn("document_text", scenarios[0])

        pipeline = RiskPipelineOrchestrator([
            DeterministicRiskAgent("financial"),
            DeterministicRiskAgent("fraud"),
            DeterministicRiskAgent("credit"),
        ])

        results = pipeline.run_dataset("veri_seti.json")
        self.assertEqual(len(results), 4)
        self.assertIn("application_id", results[0])

    def test_dataset_expected_decisions_match_rules(self):
        pipeline = RiskPipelineOrchestrator([
            DeterministicRiskAgent("financial"),
            DeterministicRiskAgent("fraud"),
            DeterministicRiskAgent("credit"),
        ])

        results = pipeline.run_dataset("veri_seti.json")
        expected_map = {
            "APP-001": "LOW_RISK",
            "APP-002": "HIGH_RISK",
            "APP-003": "MANUAL_REVIEW",
            "APP-004": "HIGH_RISK",
        }

        for result in results:
            actual = result["decision"]["decision"]
            self.assertEqual(actual, expected_map[result["application_id"]])

    def test_missing_dataset_values_force_human_review(self):
        pipeline = RiskPipelineOrchestrator([
            DeterministicRiskAgent("financial"),
            DeterministicRiskAgent("fraud"),
            DeterministicRiskAgent("credit"),
        ])

        scenario = {
            "application_id": "APP-999",
            "scenario_type": "Missing Income",
            "expected_result": "Review (Human-in-the-loop)",
            "customer_data": {
                "monthly_income_try": None,
                "requested_amount_try": 300000,
                "current_total_debt_try": 120000,
                "employment_duration_months": 4,
                "credit_history": "Unknown",
            },
            "document_text": "Gelir belgem yok, krediye ihtiyacım var.",
        }

        state = RiskPipelineState(user_request=scenario["document_text"])
        state.extracted_data = {
            "income": scenario["customer_data"].get("monthly_income_try") or 0,
            "monthly_debt": scenario["customer_data"].get("current_total_debt_try") or 0,
            "loan_amount": scenario["customer_data"].get("requested_amount_try") or 0,
            "employment_years": (scenario["customer_data"].get("employment_duration_months") or 0) / 12,
            "missing_evidence": True,
        }

        result = pipeline.run(state)

        self.assertEqual(result.risk_decision["decision"], "MANUAL_REVIEW")
        self.assertEqual(result.policy_result["status"], "MANUAL_REVIEW")
        self.assertEqual(result.authorized_action["action"], "ESCALATE_TO_HUMAN_REVIEW")


if __name__ == "__main__":
    unittest.main()
