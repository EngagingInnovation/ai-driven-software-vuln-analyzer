# Artificial Intelligence-Driven Software Vulnerability Scanner
## Vulnerability Code Analysis using AI

_a framework that can be leveraged during the Software Development Lifecycle to help fill the gap left by traditional static code analyzers_

This application is designed to automate the detection and analysis of software vulnerabilities. It comprises three primary scripts: The first processes and prepares a dataset of vulnerable code snippets*, generating embeddings for use in vector searches. The second script automates the indexing of source code into a vector search engine, enabling efficient handling of large codebases by generating and upserting code embeddings. The final script uses vector search and Large Language Models (LLMs) to identify vulnerabilities in the codebase, subsequently analyzing and reporting on these findings in a detailed format. Together, these components offer a comprehensive solution for scanning large code repositories, identifying potential vulnerabilities efficiently, and providing actionable insights for remediation.

This application addresses the limitations of traditional static code analyzers by leveraging semantic search capabilities, significantly reducing false positives and providing deeper contextual analysis, thus filling a critical gap in existing linting pipelines and enhancing software security.

\* **what are vulnerable code snippets?**
These snippets are small snapshots of code that are generally between 2 and 20 lines long. Each snippet includes a commonly known software vulnerability, such as cryptographic failures, broken access controls, and injection. 

## Getting Started

### 0. Setup Environment, API Keys and Source Code

#### application environment
Consider setting up a virtual environment for python before installing required packages. The core packages being installed are: `langchain, momento, openai, pandas, pyarrow, aiolimiter` and their dependancies. This application was built and tested with Python 3.11
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

#### saas api keys
This project uses OpenAI and Momento, both of whom provide serverless SaaS solutions and open-source SDKs for interacting with their platforms. We use these services to orchestrate the vulnerability detection with AI tools. 
* [OpenAI API Instructions](https://platform.openai.com/docs/quickstart?context=python)
* [Momento API Instructions](https://docs.momentohq.com/cache/develop/authentication/api-keys)

Store your API keys somewhere safe, like a password manager. Once saved, load them into your current session memory
```bash
# bash
export MOMENTO_API_KEY=abc123-your-entire-key-here-890xyz
export OPENAI_API_KEY=zyx098-your-actual-api-key-for-openai-123abc
```

#### source code for analysis
Since this project is about detecting and analyzing code, we'll need to download some code to get started. The directory in which we'll store the source code for this project is `./code-projects/`

```bash
# express framework (approx 9 megabytes)
git clone https://github.com/expressjs/express.git code-projects/express

# juice-shop from OWASP (approx 233 megabytes)
git clone https://github.com/juice-shop/juice-shop.git code-projects/juice-shop

# react from Meta (approx 396 megabytes)
git clone https://github.com/facebook/react.git code-projects/react
```

### 1. Convert Sample Vulnerabilities Into Embeddings
Take a look at the code in the sub-directories under `./code-vulnerable/` These are sample code files, each with a specific vulnerability identified that we'll use as our search criteria. First, we need to convert each file into a vector embedding. Here's how

```bash
# run.py is the wrapper for each of the next three primary job functions
DEBUG=true python run.py
```
program prompt in the terminal:
```md
> from within run.py, select option 1 when prompted
Select an option:
1. Vulnerable Code Embeddings Prep
2. Insert Source Code into Vector Index
3. Search for Vulnerable Code and Analyze
4. Exit
Enter choice: 1
```
After a whirl of logging output to the screen, a new file will have appeared in the root of the project which holds the embeddings for our vulnerable code collection, `vuln-code-embeddings.parquet` 

### 2. Convert Source Code to Embeddings and Store in Vector Index
```md
> from within run.py, select option 2 when prompted
> then type in 'express' as our code repository name
Select an option:
1. Vulnerable Code Embeddings Prep
2. Insert Source Code into Vector Index
3. Search for Vulnerable Code and Analyze
4. Exit
Enter choice: 2
Code repository name (like 'express' or 'react'): express 
```
Another whirl of logging output as each file is first converted into vector embeddings using an OpenAI embeddings model, and then upserted into the Momento Vector Index. 

### 3. Find the Vulnerable Source Code and run Analysis
```md
> from within run.py, select option 3 when prompted
> then type in 'express' as our code repository name 
> then 'no' for AI analysis 
Select an option:
1. Vulnerable Code Embeddings Prep
2. Insert Source Code into Vector Index
3. Search for Vulnerable Code and Analyze
4. Exit
Enter choice: 3
Code repository name (like: express or react): express
Run AI analysis after vector proximity search? (Yes/no): no
```
For the first run, selecting "no" will stop the execution after the vector search step. It is valuable to see how many files in your code base have met the criteria for further analysis. Because we are using commercial Software as a Service (SaaS) vendors, there is a cost in using their APIs. So far in this brief example, the costs for generating embeddings and storing in a serverless vector index have been very small, likely less than a penny (seriously). But, calling the OpenAI Generative AI for analysis will cost more. In this example, it could cost between 1 to 6 cents per file analysis, still pretty inexpensive but worth keeping in mind before saying 'yes' to the last question. If this is acceptable to you, select `3`, `express`, and `yes` 

The analysis step takes longer to generate, perhaps up to a minute. 

### 4. Examine the Analysis
Look for markdown formatted files in the `code-analysis/express` directory. Here is part of the analysis performed on the "express" repository from a file in the "examples" sub-directory, specifically `examples/auth/index.js`

````md
## Analysis

Yes, further investigation into fixing this source code to enhance its security is necessary. The concerns primarily revolve around broken access control, and cryptographic failures due to weak password handling and hashing mechanisms. Here are the specific lines of concern and suggested fixes:

1. **Cryptographic Failures: Weak Password Handling**
    - The password 'foobar' is hardcoded (line 37), which is a weak practice. Instead of using a hardcoded password, the application should enforce strong password policies and ensure that passwords are provided by the users during the registration process.
    - **Suggested Fix:**
        ```js
        // Instead of hardcoding the password, prompt the user to set a password during registration
        // and ensure it meets strong password criteria (length, complexity, etc.)
        ```

2. **Cryptographic Failures: Weak Hashing**
    - The `pbkdf2-password` hashing mechanism is used (line 6 and 37), which is not inherently weak, but the security depends on how it's configured (e.g., iteration count, hash function used). The code snippet does not specify these parameters, potentially leading to a weaker configuration.
    - **Suggested Fix:**
        ```js
        // Specify the iteration count and hash function explicitly to strengthen the hashing
        hash({ password: 'userInputPassword', iterations: 10000, hashFunction: 'sha256' }, function (err, pass, salt, hash) {
          // Store salt & hash
        });
        ```
````
If still running the `run.py` program, select option `4` or `enter` to exit. 

## Configuration
**config.py**  
The `config.py` file in the root of this application provides configurable parameters allowing for customization of the entire process. The configurations allow for changes in directory names, output files, and even the OpenAI models used. As you test, perhaps the most important conifugarion is the vector search score attribute. 

This score defines the line between source code files that are ignored and source code files that are selected for further analysis. If the score is too high, no files will be selected leading to the possibility of false negatives (vulnerabilities exist that were not identified). If the score is too low, you are left with the possibility of many false positives (vulnerabilities do not exist, but source files were still flagged). It will take some tweaking to find the goldilocks magic number for your project, however, after some practice the target would be roughly `0.45` 

```python
"""
THRESHOLD_SCORE (float): The minimum score from the vector search for which to consider our source code to 
be vulnerable, therefore needing further analysis with generative AI. The vector search is used to find 
potential vulnerabilities in the code. If the score from the vector search is above this threshold, the 
code will be considered vulnerable and will be passed to the generative AI for further analysis.
"""

THRESHOLD_SCORE: float = 0.47
```

## Application Scripts

### Vulnerability Code Preperation (src/vuln_code_prep.py)
This script is designed to process and prepare a dataset of vulnerable code snippets to be used as the search queries against the vector index. The output file is stored locally with the application and will be iterated over in later steps. The functionality of the script can be summarized as follows:

1. **File Processing:** The `get_file_contents` function reads the contents of a given file, extracting its code along with metadata like the file type and name. This information is crucial for identifying and categorizing vulnerabilities within the codebase.

2. **Function Extraction:** The `extract_functions_from_repo` function recursively searches for JavaScript files in the specified directory (`VULNERABLE_CODE_DIRECTORY`). It then extracts the contents of each JavaScript file, focusing on the individual functions within the codebase, preparing them for analysis.

3. **Embedding Generation and Data Compilation:** The main function orchestrates the script’s operations. It calls `extract_functions_from_repo` to gather all JavaScript functions from the target directory. These functions are then compiled into a pandas DataFrame, which also includes the relative file paths and other metadata. The script generates embeddings for each code snippet using the `get_embedding` function, facilitated by asynchronous execution to improve performance.

4. **Output and Logging:** Finally, the script saves the DataFrame, now enriched with code embeddings, to a parquet file specified by `VULNERABLE_EMBEDDINGS_FILE`. It logs the first few rows of the DataFrame to give an overview of the data processed.


### Vector Index Upsert (src/vector_idx_put.py)
This script automates the process of indexing source code for the vector search. It is structured to handle large codebases efficiently by splitting, processing, and indexing code snippets. Here's a detailed breakdown of its functionality:

1. **Code Loading and Splitting:** Using the `read_code` function, the script reads code files from the specified directory. It leverages `langchain_core` libraries to parse and split the source code into manageable chunks (Document objects), based on predefined file types like `.ts`, `.js`, etc. This step ensures that large files are broken down into smaller pieces for more effective indexing.

2. **Embedding Generation:** The `doc_embeddings` function generates embeddings for each code snippet. It assigns unique identifiers to each document by hashing its source path and keeps a count of documents to ensure unique IDs. This function then asynchronously generates embeddings for each document, creating `Item` objects for indexing.

3. **Batch Indexing:** In the `main` function, the script prepares the codebase for indexing by first deleting any existing index for the repository to ensure a fresh start. It then creates a new index and uploads the code snippets (as items) in batches to the vector index. This is facilitated by the `upsert_items` function from the utilities, which handles the actual insertion of items into the vector index.


### Search and Analyze (src/search_analyze.py)
This script is designed to perform automated security analysis on source code repositories using vector search and Large Language Models (LLMs). It operates in several steps:

1. **Index Search:** The `search_idx` function searches for vulnerabilities in the code repository's indexed data. It reads the file generated by `src/vuln_code_prep.py` which contains the vulnerable embeddings and uses these to query with a vector search client. If any code snippet's score exceeds a predefined threshold (`THRESHOLD_SCORE` in `config.py`), it's flagged for further analysis.

2. **Vulnerability Analysis with LLM:** The `analyze_code_with_llm` function takes the flagged source code files, loads them from disk, and formats them into an AI prompt, which includes a description of potential issues. This formatted prompt with the code as context is then passed to an LLM for detailed analysis, aiming to identify specific vulnerabilities and suggest fixes.

3. **Report Generation:** The `write_to_file` function generates a Markdown report for each analyzed code file, detailing the vulnerabilities and the LLM's findings.


### Utilities (src/utils.py)
The `src/utils.py` file contains a collection of helper functions crucial for the smooth operation of the code analysis application. These functions were adapted from example files provided by the SaaS vendors, OpenAI and Momento, and have been integrated into our application to facilitate tasks such as logging, generating text embeddings, managing vector index operations, and handling asynchronous tasks efficiently. The utility functions in this file play a key role in abstracting complex operations, allowing the main application logic to remain clean and focused on the core analytical process. These utilities form the backbone of the application, handling interactions with external services like OpenAI and Momento, and ensuring that the application adheres to API rate limits and operational best practices.

## Going Further
### DevSecOps Automation
This project could be modified further to execute as part of an automated continuous integration pipeline, alongside other automations that may exist for unit testing and linting. Like other automations that produce reports for further action, the GenAI produced markdown files in this application could be sent via email or added to a deployment checklist as a step needed before mergeing branches or a release to production. 

In the current itteration of this project, the entire vector index is deleted prior to recreating and repopulating each time the `vector_idx_put.py` is run. This could be changed so that upon checkin of custom application source code, only the modified files are deleted from the index, then re-run through the embedding and index insert process. 

### Fine Tune False Positives
If the `THRESHOLD_SCORE` is set low enough to avoid false negatives, your integration will begin to see more false positives. Rather than running these source files through the GenAI Analysis step each time, build a process which would remove or otherwise mark as 'ignored' the files that do not need further processing. This could simply be accomplished by removing the particular file embeddings from the vector index. But, would also require a method for reinserting the file if its been modified, like upon a new git commit. Another consideration is the addition of new vulnerable code snippets - any source files marked as 'ignored' would likely benefit from a scan against the newly added vulnerable code. 

### More Vulnerable Code
This version of the application includes 22 sample snippets for 3 common areas of well known software vulnerabilities. OWASP produces multiple Top Ten lists, with each member of the lists representing a trove of further sub-caterogizations to be explored. If there were ten vulnerable code snippets for each of the ten areas of vulnerability in the OWASP list, there would be 100 snippets to use as a search in this project.
