import json
import os
from datetime import datetime
from pathlib import Path

import openai
from PyPDF2 import PdfReader

CONTRACTS_DIR: Path = Path.cwd() / "contracts"
CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR: Path = Path.cwd() / "json"
JSON_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT: str = """
    You are a system that extracts information from reinsurance contracts 
    and inserts this information into JSON files. Use the following schema strictly
    to convert the contract information provided into JSON format. The user will
    provide the text followed by the question: "What is the JSON representation of
    this reinsurance contract?"

    Schema:

    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "treatyType": {
                "type": "string",
                "description": "Type of reinsurance treaty"
            },
            "insured": {
                "type": "string",
                "description": "Name of the insurance company being insured"
            },
            "reinsurer": {
                "type": "string",
                "description": "Name of the reinsurance company providing coverage"
            },
            "period": {
                "type": "object",
                "properties": {
                    "start": {
                        "type": "string",
                        "description": "Start date of the reinsurance period"
                    },
                    "end": {
                        "type": "string",
                        "description": "End date of the reinsurance period"
                    }
                },
                "required": [
                    "start",
                    "end"
                ],
                "description": "Period of reinsurance coverage"
            },
            "lossLayers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "layer": {
                            "type": "integer",
                            "description": "Layer number"
                        },
                        "excessOf": {
                            "type": "integer",
                            "description": "Excess amount triggering reinsurance coverage"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum coverage limit for the layer"
                        },
                        "reinsuredPercent": {
                            "type": "integer",
                            "description": "Percentage of loss reinsured for the layer"
                        }
                    },
                    "required": [
                        "layer",
                        "excessOf",
                        "limit",
                        "reinsuredPercent"
                    ]
                },
                "description": "Information about the loss layers of the reinsurance contract"
            },
            "interest": {
                "type": "string",
                "description": "Coverage interest and lines of business"
            },
            "sumInsured": {
                "type": "integer",
                "description": "Total sum insured under the reinsurance contract"
            },
            "commission": {
                "type": "object",
                "properties": {
                    "percent": {
                        "type": "integer",
                        "description": "Commission percentage"
                    },
                    "maxLossRatio": {
                        "type": "integer",
                        "description": "Maximum loss ratio for commission calculation"
                    }
                },
                "required": [
                    "percent",
                    "maxLossRatio"
                ],
                "description": "Commission details"
            },
            "exclusions": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of exclusions or risks not covered by the reinsurance"
            },
            "claimsNotification": {
                "type": "integer",
                "description": "Timeframe for claims notification in days"
            },
            "arbitrationClause": {
                "type": "string",
                "description": "Clause describing arbitration process"
            },
            "currency": {
                "type": "string",
                "description": "Currency used for the reinsurance contract"
            }
        },
        "required": [
            "treatyType",
            "insured",
            "reinsurer",
            "period",
            "lossLayers",
            "interest",
            "sumInsured",
            "commission",
            "exclusions",
            "claimsNotification",
            "arbitrationClause",
            "currency",
        ]
    }
    """  # noqa: E501


# get env vars
def get_env_variable(name: str) -> str:
    value: str | None = os.environ.get(name)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is not set")
    return value


def extract_text_from_pdf(pdf_path: Path) -> str:
    with open(pdf_path, "rb") as file:
        pdf_reader: PdfReader = PdfReader(file)
        num_pages: int = len(pdf_reader.pages)

        extracted_text: str = ""
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text: str = page.extract_text()
            extracted_text += text

    return extracted_text


def convert_text_to_json(text: str) -> dict:
    prompt: str = (
        f"Contract: {text}\n\n"
        "Q: What is the JSON representation of this reinsurance contract?"
    )

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

    for contract in CONTRACTS_DIR.iterdir():
        pdf_text: str = extract_text_from_pdf(contract)
        json_data: dict = convert_text_to_json(pdf_text)

        with open(JSON_DIR / f"{contract.stem}.json", "w") as file:
            json.dump(json_data, file, indent=4)

        print(f"{datetime.now()} - {contract.stem} converted to JSON")


if __name__ == "__main__":
    main()
