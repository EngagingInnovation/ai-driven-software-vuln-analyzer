import os
import sys
import logging
import asyncio
import pandas as pd
from typing import List, Optional

#from openai import OpenAI
from openai import AsyncOpenAI
from momento.responses.vector_index.data.search import Search

from config import ( IDX_DOCUMENT_COUNT, OPENAI_GPT_MODEL, OUTPUT_DIRECTORY, THRESHOLD_SCORE, VULNERABLE_EMBEDDINGS_FILE )
from src.utils import (
    initialize_logging,
    has_index,
    search,
    vector_client_async,
)

openai_client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
_logger = logging.getLogger("vector-code-index-search")

async def search_idx(repository_name: str, codecheck: dict) -> None:
    """Search the index using each vulnerability in the local embeddings file"""

    client = vector_client_async()

    if not await has_index(client, repository_name):
        _logger.error("Specific index does not exist")
        sys.exit(1)

    df = pd.read_parquet(f"./{VULNERABLE_EMBEDDINGS_FILE}")

    for _, row in df.iterrows():
        results = await search(client, repository_name, row['embedding'], IDX_DOCUMENT_COUNT)

        if isinstance(results, Search.Success):
            for result in results.hits:
                display_name = '/'.join(result.metadata["source"].split('/')[2:])
                _logger.debug("Source: %s, Score: %s", display_name, round(result.score, 3))

                if result.score >= THRESHOLD_SCORE:
                    issue_type = row['type'].replace('-', ' ')
                    issue_name = row['name'].replace('-', ' ')
                    source_name = result.metadata["source"]
                    language = result.metadata["language"] 

                    _logger.info("THRESHOLD HIT: Code: %s, Issue: %s - %s", display_name, issue_type, issue_name)
                    # Ensure the source_name key exists and has the required structure
                    if source_name not in codecheck:
                        codecheck[source_name] = {
                            "language": language,
                            "issues": []
                        }

                    # Prepare the issue dict
                    issue = {"type": issue_type, "name": issue_name}

                    # Add the issue to the list if it's not already present
                    # - since source files can be split into multiple parts during vector analysis, 
                    #   we want to avoid duplicate issues based on type and name for the same file
                    if issue not in codecheck[source_name]["issues"]:
                        codecheck[source_name]["issues"].append(issue)


async def analyze_code_with_llm(repository_name: str, source_name: str, language: str, issues: List[dict]) -> None:
    """Analyze the code with LLM and write the results to a file"""

    sys_template = """You are a talented software engineer and mentor for your engineering team. You are 
    deeply interested in the quality of the code produced by the team. It is a top priority for you to be
    concerned about security and the quality of code within your organization. You may be the last engineer
    to check the code before it goes to production. The team looks to you for guidance to avoid releasing
    code that is vulnerable to well known security attacks"""

    human_template = """I have been made aware that new code is our application may be insecure. This is the 
    source code that I'm concerned about. It may include issues related to the following vulnerabilities:

    {issues}
    
    ==== SOURCE CODE:
    ```{language} 
    {source_code}
    ```

    Please evaluate only the SOURCE CODE section. Would you agree that we need further investigation into fixing 
    this source code so that it can be made more secure? If so, could you please provide the line number of the code 
    of concern and an explanation of your concerns and a suggest fixes in code so that our team can take action? 
    Use at least three sentences and keep the answer as detailed as possible. If you do not agree or do not have 
    enough information, please just say that you don't know, do not try to make up an answer. Your answer should be 
    formatted in Markdown."""
    
    issues_formatted = "\n".join(f"- {issue['type']}: {issue['name']}" for issue in issues)
    code = None
    with open("./" + source_name, "r") as f:
        code = f.read()

    user_content = human_template.format(issues=issues_formatted, language=language, source_code=code) 
    _logger.debug(user_content)
    _logger.info(f"Analyzing {source_name} with LLM ...")

    try :
        completion = await openai_client.chat.completions.create(
            model=OPENAI_GPT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": sys_template,
                },
                {
                    "role": "user",
                    "content": user_content,
                }
            ],
            temperature=0.0,
        )

        findings = completion.choices[0].message.content
        write_to_file(repository_name, source_name, language, issues, findings)
        _logger.debug(findings)
        
    except Exception as e:
        _logger.error("An error occurred while analyzing code: %s, Error: %s", source_name, e)


def write_to_file(repository_name: str, source_name: str, language: str, issues: List[dict], findings: str) -> None:
    """Write the findings to a file"""

    # get rid of the first two parts of the path, then rename the file so that it sits at the top-level of the results directory
    file_name_parts = source_name.split('/')[2:]
    file_name = '-'.join(file_name_parts).rsplit('.', 1)[0] + '.md'
    output_file_path = f"{OUTPUT_DIRECTORY}/{repository_name}/{file_name}"

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    # Open the file in write mode
    with open (output_file_path, "w") as output_file:
        # Write the information to the file with Markdown formatting
        output_file.write("# Vulnerability Report\n\n") 
        output_file.write("## Input Parameters\n\n")
        output_file.write("| Key | Value |\n|-----|-------|\n")
        output_file.write(f"| Repository | {repository_name} |\n")
        output_file.write(f"| Source File | {source_name} |\n")
        output_file.write(f"| Language | {language} |\n")

        if len(issues) == 1:
            output_file.write(f"| Concern | {issues[0]['type']}: {issues[0]['name']} |\n")
        else:
            for i, issue in enumerate(issues):
                output_file.write(f"| Concern [{i+1:02d}] | {issue['type']}: {issue['name']} |\n")

        output_file.write("## Analysis\n\n")
        output_file.write(findings)
    
    _logger.info(f"Results saved to {output_file_path}")


async def main(repository_name: str, ai_analysis: bool = True) -> None:
    """
    Main entry point for the script.
    
    This function performs the following tasks:
    
    1. Calls the search_idx function to gather a dictionary of file names and their associated issues.
    2. If ai_analysis is True, it then creates a list of tasks by calling the analyze_code_with_llm function for each file.
    3. Finally, it waits for all of the tasks to complete using asyncio.gather.
    
    Arguments:
        repository_name: The name of the Git repository to analyze.
        ai_analysis: A boolean indicating whether or not to perform analysis with LLM.
    """
    code_analysis = {}  # type: Dict[str, Dict[str, Any]]
    tasks = []          # type: List[asyncio.Task]
    
    await search_idx(repository_name, code_analysis)
    _logger.info(f"{len(code_analysis)} files selected for further analysis")
    for source_name, data in code_analysis.items():
        _logger.info(f"Source: {source_name}, Issue Type: {data['issues'][0]['type']}")

    if not ai_analysis:
        return

    _logger.info("Analyzing code with LLM ...")
    for source_name, data in code_analysis.items():
        tasks.append(
            analyze_code_with_llm(repository_name, source_name, data["language"], data["issues"])
        )
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python idx_search.py <directory_name>")
        sys.exit(1)

    initialize_logging()
    directory = sys.argv[1]
    asyncio.run(main(directory))
