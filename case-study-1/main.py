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
    to convert the information provided into JSON format. The user will
    provide the interaction and you will use it to:
    1. Extract the claim number (claim_id)
    2. Extract the policy number (policy_id)
    3. Rate the likelihood of the claim being fraudulent with 1 being low and 3
    being high (fraud_likelihood) with reasoning (fraud_likelihood_reasoning)
    4. Determine the emotional state of the claimant (claimant_emotion) with reasoning
    (claimant_emotion_reasoning)
    5. Summarise the claim based on the information provided (claim_summary)
    6. Determine if further assessment is required (further_assessment_required)
    with reasoning (further_assessment_reasoning)

    Schema:

    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "claim_id": {
                "type": "string",
                "description": "The claim number"
            },
            "policy_id": {
                "type": "string",
                "description": "The policy number"
            },
            "fraud_likelihood": {
                "type": "integer",
                "minimum": 1,
                "maximum": 3,
                "description": "The likelihood of the claim being fraudulent with 1 being low and 3 being high"
            },
            "reason_for_fraud_rating": {
                "type": "string",
                "description": "The reasoning behind the fraud rating"
            },
            "claimant_emotion": {
                "type": "string",
                "description": "The emotional state of the claimant"
            },
            "reason_for_emotion": {
                "type": "string",
                "description": "The reasoning behind determining the claimant's emotional state"
            },
            "claim_summary": {
                "type": "string",
                "description": "Summary of the claim based on the information provided"
            },
            "further_assessment_required": {
                "type": "boolean",
                "description": "Determine if further assessment is required"
            },
            "reason_for_further_assessment": {
                "type": "string",
                "description": "The reasoning behind the need for further assessment"
            }
        },
        "required": [
            "claim_id",
            "policy_id",
            "fraud_likelihood",
            "reason_for_fraud_rating",
            "claimant_emotion",
            "reason_for_emotion",
            "claim_summary",
            "further_assessment_required",
            "reason_for_further_assessment"
        ]
    }

    """  # noqa: E501


# get env vars
def get_env_variable(name: str) -> str:
    value: str | None = os.environ.get(name)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is not set")
    return value


def assess_claim(text: str) -> dict:
    prompt: str = f"Claim: {text}"

    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {
                "role": "user",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": prompt},
        ],
    )

    return json.loads(gpt_response.choices[0].message.content)


def main() -> None:
    OPENAI_API_KEY: str = get_env_variable("OPENAI_API_KEY")

    openai.api_key = OPENAI_API_KEY

    for claim in (CLAIMS_DIR).iterdir():
        with open(claim, "r") as file:
            claim_data: str = file.read()

        assessment_json: str = assess_claim(claim_data)

        with open(ASSESSMENT_DIR / f"{claim.stem}.json", "w") as file:
            json.dump(assessment_json, file, indent=4)

        print(f"{datetime.now()} - {claim.stem} assessed.")


if __name__ == "__main__":
    main()
