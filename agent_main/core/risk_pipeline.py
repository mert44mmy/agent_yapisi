import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RiskPipelineState:
    user_request: str
    extracted_data: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    risk_decision: dict[str, Any] = field(default_factory=dict)
    policy_result: dict[str, Any] = field(default_factory=dict)
    authorized_action: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)

    def update(self, agent_name: str, updates: dict[str, Any]) -> None:
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.history.append({"agent": agent_name, "updates": updates})


class InputValidator:
    """Deterministic validation layer: removes sensitive values and validates the request."""

    @staticmethod
    def normalize(text: str) -> str:
        masked = re.sub(r"(\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b)", "[EMAIL]", text, flags=re.IGNORECASE)
        masked = re.sub(r"(\b\d{11}\b)", "[TCKN]", masked)
        masked = re.sub(r"(\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b)", "[CARD]", masked, flags=re.IGNORECASE)
        return masked.strip()

    @staticmethod
    def validate(text: str) -> dict[str, Any]:
        normalized = InputValidator.normalize(text)
        return {
            "validated": bool(normalized and len(normalized) > 10),
            "masked_text": normalized,
            "data_minimization_applied": True,
        }


class DocumentAnalyzer:
    """Extracts simple structured facts from natural-language input."""

    @staticmethod
    def extract(text: str) -> dict[str, Any]:
        numbers = re.findall(r"\d+(?:\.\d+)?", text)
        income = float(numbers[0]) if numbers else 0.0
        debt = float(numbers[1]) if len(numbers) > 1 else 0.0
        loan_amount = float(numbers[2]) if len(numbers) > 2 else 0.0
        employment_years = float(numbers[3]) if len(numbers) > 3 else 0.0
        prior_fraud = "fraud" in text.lower() and "no prior fraud" in text.lower()
        details = {
            "income": income,
            "monthly_debt": debt,
            "loan_amount": loan_amount,
            "employment_years": employment_years,
            "prior_fraud": prior_fraud,
            "prompt_injection_detected": "SYSTEM OVERRIDE" in text.upper(),
            "missing_evidence": False,
        }
        if income and debt:
            details["debt_to_income_ratio"] = round(debt / income, 4)
        if not income:
            details["missing_evidence"] = True
        return details


class DeterministicRiskAgent:
    """A deterministic agent optimized for finance and security rule checks."""

    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.name = f"{agent_type}_agent"

    def run(self, state: RiskPipelineState) -> dict[str, Any]:
        extracted = state.extracted_data or DocumentAnalyzer.extract(state.user_request)
        state.extracted_data = extracted

        if self.agent_type == "financial":
            ratio = extracted.get("debt_to_income_ratio", 0)
            score = 0
            if ratio > 0.7:
                score += 4
            elif ratio > 0.45:
                score += 2
            if extracted.get("loan_amount", 0) > 500000:
                score += 2
            elif extracted.get("loan_amount", 0) > 250000:
                score += 1
            return {
                "financial_evidence": {
                    "debt_to_income_ratio": ratio,
                    "loan_amount": extracted.get("loan_amount", 0),
                    "risk_score": score,
                    "status": "HIGH" if score >= 3 else "LOW",
                }
            }

        if self.agent_type == "fraud":
            prior_fraud = bool(extracted.get("prior_fraud", False))
            prompt_injection = bool(extracted.get("prompt_injection_detected", False))
            score = 3 if prior_fraud else 0
            if prompt_injection:
                score += 5
            return {
                "fraud_evidence": {
                    "prior_fraud": prior_fraud,
                    "prompt_injection_detected": prompt_injection,
                    "risk_score": score,
                    "status": "HIGH" if score >= 3 else "LOW",
                }
            }

        if self.agent_type == "credit":
            years = extracted.get("employment_years", 0)
            income = extracted.get("income", 0)
            score = 0
            if years < 1:
                score += 2
            if income < 20000:
                score += 1
            if extracted.get("missing_evidence", False):
                score += 3
            return {
                "credit_evidence": {
                    "employment_years": years,
                    "income": income,
                    "risk_score": score,
                    "status": "HIGH" if score >= 3 else "LOW",
                }
            }

        return {f"{self.agent_type}_evidence": {"risk_score": 0, "status": "LOW"}}


class DecisionOrchestrator:
    """Aggregates evidence from parallel risk agents."""

    @staticmethod
    def aggregate(state: RiskPipelineState) -> dict[str, Any]:
        evidence = state.evidence or {}
        score = 0
        reasons: list[str] = []

        for agent_key in ("financial_evidence", "fraud_evidence", "credit_evidence"):
            item = evidence.get(agent_key, {})
            score += int(item.get("risk_score", 0))
            if item.get("status") == "HIGH":
                reasons.append(agent_key)

        if state.extracted_data.get("prompt_injection_detected"):
            decision = "HIGH_RISK"
        elif state.extracted_data.get("missing_evidence"):
            decision = "MANUAL_REVIEW"
        elif score >= 7:
            decision = "HIGH_RISK"
        elif score >= 4:
            decision = "MANUAL_REVIEW"
        else:
            decision = "LOW_RISK"

        return {
            "decision": decision,
            "score": score,
            "reasons": reasons,
        }


class PolicyValidator:
    """Deterministic policy layer that converts evidence into a safe action decision."""

    @staticmethod
    def validate(risk_decision: dict[str, Any]) -> dict[str, Any]:
        decision = risk_decision.get("decision", "LOW_RISK")
        if decision == "HIGH_RISK":
            return {"status": "HIGH_RISK", "checks_passed": False, "reason": "High-risk signals found."}
        if decision == "MANUAL_REVIEW":
            return {"status": "MANUAL_REVIEW", "checks_passed": False, "reason": "Requires human validation."}
        return {"status": "LOW_RISK", "checks_passed": True, "reason": "No policy violations detected."}


class AuthorizedActionLayer:
    """Least-privilege execution layer for approved decisions."""

    @staticmethod
    def decide(policy_result: dict[str, Any]) -> dict[str, Any]:
        status = policy_result.get("status", "LOW_RISK")
        if status == "LOW_RISK":
            return {
                "action": "APPROVE_APPLICATION",
                "permissions": ["read_applicant", "create_record", "notify_customer"],
            }
        if status == "MANUAL_REVIEW":
            return {
                "action": "ESCALATE_TO_HUMAN_REVIEW",
                "permissions": ["read_only", "escalate_case"],
            }
        return {
            "action": "BLOCK_APPLICATION",
            "permissions": ["read_only", "raise_security_alert"],
        }


def load_scenarios(file_name: str) -> list[dict[str, Any]]:
    base_dir = Path(__file__).resolve().parent.parent
    path = base_dir / file_name
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


class RiskPipelineOrchestrator:
    def __init__(self, agents: list[DeterministicRiskAgent]):
        self.agents = agents

    def run(self, state: RiskPipelineState) -> RiskPipelineState:
        validation = InputValidator.validate(state.user_request)
        state.extracted_data = DocumentAnalyzer.extract(state.user_request)
        state.update("input_validator", {"validation": validation})

        for agent in self.agents:
            updates = agent.run(state)
            state.evidence.update(updates)
            state.update(agent.name, {"evidence": state.evidence})

        state.risk_decision = DecisionOrchestrator.aggregate(state)
        state.policy_result = PolicyValidator.validate(state.risk_decision)
        state.authorized_action = AuthorizedActionLayer.decide(state.policy_result)

        state.update(
            "policy_validator",
            {
                "risk_decision": state.risk_decision,
                "policy_result": state.policy_result,
                "authorized_action": state.authorized_action,
            },
        )
        return state

    def run_dataset(self, dataset_file: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for scenario in load_scenarios(dataset_file):
            document_text = scenario.get("document_text", "")
            state = RiskPipelineState(user_request=document_text)
            state.extracted_data = {
                "income": scenario.get("customer_data", {}).get("monthly_income_try") or 0,
                "monthly_debt": scenario.get("customer_data", {}).get("current_total_debt_try") or 0,
                "loan_amount": scenario.get("customer_data", {}).get("requested_amount_try") or 0,
                "employment_years": (scenario.get("customer_data", {}).get("employment_duration_months") or 0) / 12,
                "prior_fraud": False,
            }
            if state.extracted_data["income"]:
                state.extracted_data["debt_to_income_ratio"] = round(
                    state.extracted_data["monthly_debt"] / state.extracted_data["income"], 4
                )

            if "SYSTEM OVERRIDE" in document_text.upper():
                state.extracted_data["prompt_injection_detected"] = True

            for agent in self.agents:
                updates = agent.run(state)
                state.evidence.update(updates)

            state.risk_decision = DecisionOrchestrator.aggregate(state)
            state.policy_result = PolicyValidator.validate(state.risk_decision)
            state.authorized_action = AuthorizedActionLayer.decide(state.policy_result)

            result = {
                "application_id": scenario.get("application_id"),
                "scenario_type": scenario.get("scenario_type"),
                "expected_result": scenario.get("expected_result"),
                "decision": state.risk_decision,
                "policy_result": state.policy_result,
                "authorized_action": state.authorized_action,
                "matched_expected_result": False,
            }
            results.append(result)

        return results


if __name__ == "__main__":
    demo_state = RiskPipelineState(
        user_request=(
            "Applicant income 35000, monthly debt 1200, no prior fraud, "
            "employment 2 years, loan amount 5000"
        )
    )

    pipeline = RiskPipelineOrchestrator(
        [
            DeterministicRiskAgent("financial"),
            DeterministicRiskAgent("fraud"),
            DeterministicRiskAgent("credit"),
        ]
    )
    result = pipeline.run(demo_state)
    print(result.risk_decision)
    print(result.policy_result)
    print(result.authorized_action)

    dataset_results = pipeline.run_dataset("veri_seti.json")
    for item in dataset_results:
        print(item["application_id"], item["decision"], item["policy_result"], item["authorized_action"])
