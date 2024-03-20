# config.py
"""
Configuration for the code analysis application.

Attributes:
    PROJECT_CODE_DIRECTORY (str): The name of the directory containing code projects to be analyzed. This 
    directory should contain subdirectories with the code to be analyzed. Each subdirectory will be treated 
    as a separate project.

    IDX_DOCUMENT_COUNT (int): The number of documents to return from the vector search. This is a tunable 
    parameter that can be adjusted to see how it affects the performance of the project. Depending on the 
    value of the THRESHOLD_SCORE, this number may need to be adjusted to see how it affects the results.

    OPENAI_EMBEDDING_MODEL (str): The model from OpenAI to use for generating text embeddings. This model 
    generates text embeddings based on the input text. It is used to generate embeddings for the code in 
    the PROJECT_CODE_DIRECTORY. The smaller the model, the fewer the embeddings will be.

    OPENAI_GPT_MODEL (str): The model from OpenAI to use for the generative AI analysis. This model is used 
    to generate code based on the code in the PROJECT_CODE_DIRECTORY. The larger the model, the more 
    comprehensive the generated code will be.

    OUTPUT_DIRECTORY (str): The directory name where the results from the generative AI analysis will be 
    stored. The generated code will be saved in this directory, as parquet files.

    SOURCE_CHUNK_SIZE (int): Source code will be split into chunks of this size to stay within the token limit 
    of the embedding model. This is a tunable parameter that can be adjusted to see how it affects the 
    performance of the project.

    THRESHOLD_SCORE (float): The minimum score from the vector search for which to consider our source code to 
    be vulnerable, therefore needing further analysis with generative AI. The vector search is used to find 
    potential vulnerabilities in the code. If the score from the vector search is above this threshold, the 
    code will be considered vulnerable and will be passed to the generative AI for further analysis.

    VULNERABLE_CODE_DIRECTORY (str): Directory name containing the vulnerable code that will be used as the 
    search query in the vector index. This directory should contain code that is vulnerable and should be used 
    as the search query in the vector index. This code will be fed into the vector search to find potential 
    vulnerabilities.

    VULNERABLE_EMBEDDINGS_FILE (str): The file name of the parquet that will contain the embeddings of the 
    vulnerable code. The generated embeddings for the code in the VULNERABLE_CODE_DIRECTORY will be saved in 
    this parquet file.
"""

PROJECT_CODE_DIRECTORY: str = "code-projects"

IDX_DOCUMENT_COUNT: int = 7

OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

OPENAI_GPT_MODEL: str = "gpt-4-turbo-preview"

OUTPUT_DIRECTORY: str = "code-analysis"

SOURCE_CHUNK_SIZE: int = 15000

THRESHOLD_SCORE: float = 0.47

VULNERABLE_CODE_DIRECTORY: str = "code-vulnerable"

VULNERABLE_EMBEDDINGS_FILE: str = "vuln-code-embeddings.parquet"
