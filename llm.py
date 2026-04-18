import json
import os
import re
from pathlib import Path
import anthropic

env_path = Path(__file__).parent.parent / ".env_legal_ai"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                match = re.match(r'export\s+(\w+)=(.+)', line)
                if match:
                    key, val = match.groups()
                    os.environ.setdefault(key, val.strip('"'))

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = anthropic.Anthropic(api_key=api_key)

MODEL = "claude-sonnet-4-20250514"


def llm_json(system: str, user: str) -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    
    text = response.content[0].text
    
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    
    return json.loads(text.strip())