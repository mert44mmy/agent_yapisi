import json
from pathlib import Path

from core.risk_pipeline import (
    RiskPipelineOrchestrator,
    DeterministicRiskAgent,
)


def read_user_request(path=None) -> str:
    base_dir = Path(__file__).resolve().parent
    file_path = Path(path) if path else base_dir / "input.txt"
    if not file_path.is_absolute():
        file_path = base_dir / file_path
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def translate_decision(value: str) -> str:
    mapping = {
        "LOW_RISK": "Düşük Risk",
        "MANUAL_REVIEW": "Manuel İnceleme",
        "HIGH_RISK": "Yüksek Risk",
        "APPROVE_APPLICATION": "Başvuruyu Onayla",
        "ESCALATE_TO_HUMAN_REVIEW": "İnsan İncelemeye Yönlendir",
        "BLOCK_APPLICATION": "Başvuruyu Engelle",
    }
    return mapping.get(value, value)


def format_policy(policy: dict) -> str:
    status = policy.get("status", "")
    reason = policy.get("reason", "")
    return f"Durum: {translate_decision(status)} | Açıklama: {reason}"


def format_action(action: dict) -> str:
    label = action.get("action", "")
    permissions = ", ".join(action.get("permissions", [])) or "-"
    return f"Eylem: {translate_decision(label)} | İzinler: {permissions}"


def main():
    dataset_path = Path(__file__).resolve().parent / "veri_seti.json"
    agents = [
        DeterministicRiskAgent("financial"),
        DeterministicRiskAgent("fraud"),
        DeterministicRiskAgent("credit"),
    ]

    orchestrator = RiskPipelineOrchestrator(agents)
    results = orchestrator.run_dataset(str(dataset_path))

    print("\n=== VERİ SETİ DEĞERLENDİRME SONUÇLARI ===")
    for index, item in enumerate(results, start=1):
        actual = item["decision"]["decision"]
        expected = item["expected_result"]
        matched = (
            ("Decision" in expected and actual in expected)
            or ("Review" in expected and actual in expected)
            or ("Block" in expected and actual in expected)
        )
        item["matched_expected_result"] = matched

        print(f"\n[{index}] {item['application_id']} - {item['scenario_type']}")
        print(f"  Beklenen: {expected}")
        print(f"  Gerçek: {translate_decision(actual)}")
        print(f"  Eşleşme: {'Evet' if matched else 'Hayır'}")
        print(f"  Politika: {format_policy(item['policy_result'])}")
        print(f"  Yetkili Aksiyon: {format_action(item['authorized_action'])}")


if __name__ == "__main__":
    main()
