import json
import os
from datetime import datetime
from pathlib import Path

import openai

CLAIMS_DIR: Path = Path.cwd() / "claims"
CLAIMS_DIR.mkdir(parents=True, exist_ok=True)
ASSESSMENT_DIR: Path = Path.cwd() / "assessment"
ASSESSMENT_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT: str = """
You are a system that extracts information from claims reporting interactions 
and inserts this information into JSON files. Use the following schema strictly 
to convert the information provided into JSON format. The user will provide the 
interaction and you will use it to:

Extract the claim number (claim_id)
Extract the policy number (policy_id)
Identify any inconsistencies in the information. For example, a police report 
indicating brake marks, but the claimaint indicating they were stationary. (inconsistencies)  
Determine the emotional state of the claimant (claimant_emotion) with 
supporting information (claimant_emotion_reasoning)
Summarise the claim based on the information provided (claim_summary)
Determine if further assessment is required (further_assessment_required) 
with supporting information (further_assessment_reasoning)

Provide only the valid json output and nothing else.

Schema:
"""  # noqa: E501


# get env vars
def get_env_variable(name: str) -> str:
    value: str | None = os.environ.get(name)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is not set")
    return value


def assess_claim(system_prompt: str, claim_context: str) -> dict:
    prompt: str = f"Claim: {claim_context}"

    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ],
    )

    return json.loads(gpt_response.choices[0].message.content)


def main() -> None:
    # read json as raw string
    with open("schema.json", "r") as file:
        SCHEMA: str = file.read()

    system_prompt = f"{SYSTEM_PROMPT}{SCHEMA}"

    OPENAI_API_KEY: str = get_env_variable("OPENAI_API_KEY")

    openai.api_key = OPENAI_API_KEY

    for claim in (CLAIMS_DIR).iterdir():
        with open(claim, "r") as file:
            claim_context: str = file.read()

        assessment_json: str = assess_claim(system_prompt, claim_context)

        with open(ASSESSMENT_DIR / f"{claim.stem}.json", "w") as file:
            json.dump(assessment_json, file, indent=4)

        print(f"{datetime.now()} - {claim.stem} assessed.")


if __name__ == "__main__":
    main()
