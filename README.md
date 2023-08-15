# Case Studies for ActuaryGPT: Applications of Large Language Models to Insurance and Actuarial Work

This repository is a companion to the ActuaryGPT paper and consists of multiple case studies that utilize the OpenAI API and other libraries to perform various tasks.

## Case Study 1: Claims Reporting

In this case study, GPT 4 is used to parse engagements with policyholders during the claims process to determine the sentiment of the engagement, emotional state of the claimant, and identify any inconsistencies with the claim information.

It is important to note that the LLM serves as an automation tool in this respect, and is not intended to replace human claims handlers, or to be the final decider on fraud or further
engagements. Rather, it is intended to provide a tool to assist claims handlers in their work by parsing the information provided by the claimant and providing a summary of the engagement and a set of indicators to guide further work.

## Case Study 2: Cybersecurity News Analysis

In this case study GPT 4 summarises a collection of news snippets to identify emerging cyber risks. The script conducts an automated custom Google Search for recent articles using a list of search terms. It extracts the metadata of the search results and uses `GPT-4` to generate a detailed summary of the notable emerging cyber risks, themes, and trends identified.

## Case Study 3: Regulatory Knowledgebase

As described in the paper, LLMs are not able to digest large volumes of regulatory documents so in this case study a knowledgebase of regulatory documents is constructed using vector embeddings of their contents.

Leveraging the ”OP” stack, so named because it uses the OpenAI API and the Pinecone database, the knowledgebase is constructed as follows. 

- Regulatory documents are fed to the OpenAI embedding endpoint to generate vector
embeddings of the documents.
- These embeddings are then stored in the Pinecone database. The Pinecone database is
a vector database that allows for fast vector searches.
- On top of this, a website is built that allows the user to input a text query which is then used to search the vector database. The vector embedding of the text query is then compared
to the vector embeddings of the regulatory documents and the most similar documents are returned to the user.
- These documents are then used as context for the LLM to generate a response to the user’s query. This allows the LLM to answer questions within the context of the regulatory documents provided, allowing for more accurate and relevant responses.

## Case Study 4: Reinsurance Contract Analysis

Reinsurance contracts are critical documents that are often lengthy and complex, making them time-consuming to analyze and understand, not to mention, exposing the insurer to significant risk if all contracts are not well understood.

In this case study, an LLM is used to automate the process of extracting structured data from reinsurance contracts, such as the type of reinsurance, the reinsurer, the reinsured, the coverage period, and the premium amount. This structured data can then be used to populate a database or spreadsheet for further analysis.

## Prerequisites

- Python 3.11 (not tested on earlier versions)
- OpenAI API Key
- Google Custom Search API Key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/cbalona/actuarygpt-code.git
cd actuarygpt-code
```

Setup the virtual environment:

```bash
make setup
```

Install the dependencies:

```bash
make
```

You will need to set the following environment variables:
| Variable | Description | Applicable Case Study |
| --- | --- | --- |
| OPENAI_API_KEY | Your OpenAI API key | Needed for all case studies. |
| GOOGLE_CUSTOMSEARCH_API_KEY | Your Google Custom Search API key | Needed for Case Study 2. |
| GOOGLE_CUSTOMSEARCH_CX_KEY | Your Google Custom Search CX key | Needed for Case Study 2. |


## Usage

Navigate to the appropriate case study directory (`case-study-1`, `case-study-2`, or `case-study-4`).

Run the `main.py` script:

```bash
python main.py
```

## License

This project is licensed under the terms of the CC-BY 4.0 license. See [LICENSE](LICENSE) for details.
