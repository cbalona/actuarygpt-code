import json
import os
from datetime import datetime
from pathlib import Path

import openai
import requests

# set some paths
WEATHER_NEWS_DIR: Path = Path().cwd() / "weather-news"
WEATHER_NEWS_DIR.mkdir(parents=True, exist_ok=True)


# get env vars
def get_env_variable(name: str) -> str:
    value: str | None = os.environ.get(name)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is not set")
    return value


def main() -> None:
    OPENAI_API_KEY: str = get_env_variable("OPENAI_API_KEY")
    GOOGLE_API_KEY: str = get_env_variable("GOOGLE_CUSTOMSEARCH_API_KEY")
    GOOGLE_CX: str = get_env_variable("GOOGLE_CUSTOMSEARCH_CX_KEY")

    openai.api_key = OPENAI_API_KEY

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
        "cx": GOOGLE_CX,
        "key": GOOGLE_API_KEY,
        "num": 10,  # number of results per page
        "lr": "lang_en",  # limit results to English language
        "filter": 1,  # duplicate content filter
        "dateRestrict": "m1",  # last 1 months
        "cr": "countryUS",  # limit results to US
        "start": 1,  # start at page 1
    }

    # get top 10 results
    WEATHER_NEWS_DIR.mkdir(parents=True, exist_ok=True)

    search_results: list[dict] = []
    try:
        search_response: requests.Response = requests.get(search_url, params=params)
        search_response.raise_for_status()
        search_results = search_response.json()["items"]
        # dump results
        with open(
            WEATHER_NEWS_DIR / f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json",
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

    USER_PROMPT: str = "\n".join(
        [f"{title}: {description}" for title, description in zip(titles, descriptions)]
    )

    SYSTEM_PROMPT: str = """
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

    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": USER_PROMPT},
        ],
    )

    print(gpt_response.choices[0].message.content)  # type: ignore


if __name__ == "__main__":
    main()
