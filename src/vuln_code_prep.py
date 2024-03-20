import asyncio
import os
import logging
import pandas as pd
from pathlib import Path

from config import ( VULNERABLE_CODE_DIRECTORY, VULNERABLE_EMBEDDINGS_FILE )
from src.utils import (
    initialize_logging,
    get_embedding
)

_logger = logging.getLogger("vector-code-index-vuln-prep")

def get_file_contents(filepath):
    """ Extract file's contents and name derived from its path. """
    with open(filepath, "r") as f:
        contents = f.read()

    file_name, _ = os.path.splitext(os.path.basename(filepath))
    file_type = os.path.basename(os.path.dirname(filepath))

    return {
        'code': contents,
        'type': file_type,
        'name': file_name,
        'filepath': filepath,
    }


def extract_functions_from_repo(code_root):
    """ Extract all .js functions from the repository. """
    js_files = list(code_root.glob('**/*.js'))
    functions = [get_file_contents(str(js_file)) for js_file in js_files]

    return functions


async def main() -> None:
    # Get the path to our vulnerable code repository
    code_root = Path(f"./{VULNERABLE_CODE_DIRECTORY}")

    # Extract all functions from our vulnerable code repository
    all_funcs = extract_functions_from_repo(code_root)

    # Create a DataFrame to hold all our vulnerable functions and metadata (including embeddings)
    #  - remove full filepaths from dataframe and only keep relative paths
    df = pd.DataFrame(all_funcs)
    df['filepath'] = df['filepath'].map(lambda x: Path(x).relative_to(code_root)).astype(str)
    df['code'] = df['code'].astype(str)
    df['type'] = df['type'].astype(str)
    df['name'] = df['name'].astype(str)

    # Get the embeddings for all functions in the dataframe
    tasks = [get_embedding(code) for code in df['code']]
    embeddings = await asyncio.gather(*tasks)

    # Add the embeddings to the dataframe
    df['embedding'] = embeddings

    # Save the dataframe to disk
    df.to_parquet(f"./{VULNERABLE_EMBEDDINGS_FILE}")
    _logger.debug(f"Saved dataframe to: {VULNERABLE_EMBEDDINGS_FILE}")

    _logger.info(f"Total number of vulnerable functions in file: {len(df)}")
    _logger.info(f"First 5 rows of dataframe:\n{df.head()}")


if __name__ == "__main__":
    initialize_logging()
    asyncio.run(main())