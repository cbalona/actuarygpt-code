import json
import os
from datetime import datetime
from pathlib import Path

import openai
import requests


# get env vars
def get_env_variable(name: str) -> str:
    value: str | None = os.environ.get(name)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is not set")
    return value


# news scraper
def get_news(
    google_cx: str, google_api_key: str, save_dir: Path
) -> tuple[list[str], list[str]]:
    # define search terms
    must_include_search_terms: list[str] = [
        '"cybersecurity risk"',
        '"cyber threat"',
        '"data breach"',
        '"ransomware attack"',
        '"phishing"',
        '"malware"',
        '"cyber attack"',
        '"information security"',
        '"cyber insurance"',
        '"data protection"',
        '"privacy regulations"',
        '"data security regulations"',
        '"cybersecurity legislation"',
        '"GDPR compliance"',
        '"HIPAA compliance"',
        '"PCI DSS compliance"',
        '"regulatory requirements for insurers"',
        '"cyber risk management"',
        '"cyber resilience"',
        '"incident response"',
        '"security breach"',
        '"cyber risk assessment"',
        '"cybersecurity best practices"',
    ]
    q: str = " OR ".join(must_include_search_terms)

    # set up custom search
    search_url: str = "https://www.googleapis.com/customsearch/v1"
    params: dict[str, str | int] = {
        "q": q,
        "cx": google_cx,
        "key": google_api_key,
        "num": 10,  # number of results per page
        "lr": "lang_en",  # limit results to English language
        "filter": 1,  # duplicate content filter
        "dateRestrict": "m1",  # last 1 months
        "cr": "countryUS",  # limit results to US
        "start": 1,  # start at page 1
    }

    # get top 10 results
    search_results: list[dict] = []
    try:
        search_response: requests.Response = requests.get(search_url, params=params)
        search_response.raise_for_status()
        search_results = search_response.json()["items"]
        # dump results
        with open(
            Path(save_dir) / f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json",
            "w",
        ) as f:
            json.dump(search_results, f)
    except Exception as e:
        print(f"Error occurred while processing: {e}")

    # get titles and descriptions
    titles: list[str] = []
    descriptions: list[str] = []
    for article in search_results:
        try:
            titles.append(article["pagemap"]["metatags"][0]["og:title"])
            descriptions.append(article["pagemap"]["metatags"][0]["og:description"])
        except Exception as e:
            print(f"Error occurred while processing article {article['link']}: {e}")

    return titles, descriptions


def summary_prompt(titles: list[str], descriptions: list[str], save_dir: str) -> str:
    user_prompt: str = "\n".join(
        [f"{title}: {description}" for title, description in zip(titles, descriptions)]
    )

    system_prompt: str = """
    I am a risk analyst for a large insurance company. I am tasked with
    identifying emerging cyber risks that could impact our business.
    I have collected snippets of a series of news articles.
    I'd like you to identify a few notable emerging cyber risks, themes, and
    trends and list them. Don't name any companies or individuals.

    Following this, produce a short summary identifying the emerging risks common
    in all the articles. The summary should be of sufficient length and detail 
    that a Board member can understand the risks and opportunities and make an 
    informed decision on how to proceed.
    This summary will be included in a report to the Board of Directors.
    """

    # first get the summary
    summary: str = (
        openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": system_prompt,
                },
                {"role": "user", "content": user_prompt},
            ],
        )
        .choices[0]
        .message.content
    )

    with open(Path(save_dir) / "summary.txt", "w") as f:
        f.write(summary)

    return summary


def action_points_prompt(summary: str, save_dir: Path) -> str:
    follow_up_prompt: str = f"""
    List three action points that the Board should consider in order of priority.
    List not more than three points.
    Seperate each action point with "\n".
    Each action point should be a single complete sentence.

    For example, if the summary states that "the Board should consider cyber
    security providers", then the action point would be "Provide a high-level
    project plan to discover and evaluate cyber security providers, including
    some information on how to evaluate them."
    """

    action_points: str = (
        openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": summary},
                {
                    "role": "user",
                    "content": follow_up_prompt,
                },
            ],
        )
        .choices[0]
        .message.content
    )

    with open(Path(save_dir) / "action_points.txt", "w") as f:
        f.write(action_points)

    return action_points


def fulfill_actions_prompt(action_points: str, save_dir: Path) -> None:
    initial_instruction: str = """
    Produce a project plan for the following action point.
    """

    action_points: list[str] = action_points.split("\n")
    for i, action_point in enumerate(action_points):
        action: str = (
            openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": initial_instruction,
                    },
                    {
                        "role": "user",
                        "content": action_point,
                    },
                ],
            )
            .choices[0]
            .message.content
        )
        print(f"{datetime.now()} - action {i} processed.")
        with open(Path(save_dir) / f"action_{i}.txt", "w") as f:
            f.write(action)


def main() -> None:
    Path("news").mkdir(parents=True, exist_ok=True)
    Path("output").mkdir(parents=True, exist_ok=True)

    titles, descriptions = get_news(
        google_cx=get_env_variable("GOOGLE_CUSTOMSEARCH_CX_KEY"),
        google_api_key=get_env_variable("GOOGLE_CUSTOMSEARCH_API_KEY"),
        save_dir="news",
    )

    # first get the summary
    summary: str = summary_prompt(titles, descriptions, save_dir="output")
    print(f"{datetime.now()} - summary produced.")

    # then process the summary
    action_points: str = action_points_prompt(summary, save_dir="output")
    print(f"{datetime.now()} - action points produced.")

    # finally, for each action point, ask GPT to fulfill it
    fulfill_actions_prompt(action_points, save_dir="output")
    print(f"{datetime.now()} - actions fulfilled.")


if __name__ == "__main__":
    OPENAI_API_KEY: str = get_env_variable("OPENAI_API_KEY")

    openai.api_key = OPENAI_API_KEY

    main()
