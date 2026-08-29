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


if __name__ == "__main__":
    unittest.main()
