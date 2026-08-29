import json
from pathlib import Path
from core.llm import call_llm
from core.utils import clean_json_response


class BaseAgent:
    name = "base_agent"
    prompt_file = ""

    def run(self, state):
        prompt = self._build_prompt(state)
        response = call_llm(prompt)
        return clean_json_response(response)

    def _build_prompt(self, state) -> str:
        template = Path(self.prompt_file).read_text(encoding="utf-8")
        return template.replace("{state}", json.dumps(state.to_dict(), indent=2, ensure_ascii=False))
