import json
import os
from config import OUTPUT_DIR


class SequentialOrchestrator:
    def __init__(self, agents):
        self.agents = agents

    def run(self, state):
        for agent in self.agents:
            print(f"\n--- Running {agent.name} ---")
            updates = agent.run(state)
            state.update(agent.name, updates)
            self._save_step(agent.name, state.to_dict())
        return state

    def _save_step(self, agent_name: str, state: dict) -> None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"{agent_name}.json")
        with open(path, "w", encoding="utf-8") as file:
            json.dump(state, file, indent=2, ensure_ascii=False)
