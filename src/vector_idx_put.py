import asyncio
import os
import sys
import hashlib
import logging
from typing import List, Optional

# LANGCHAIN LIBS TO HELP SPLIT THE CODE INTO SMALLER DOCUMENTS
from langchain_core.documents.base import Document
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language,
)

from momento.requests.vector_index import Item

from config import (PROJECT_CODE_DIRECTORY, SOURCE_CHUNK_SIZE)
from src.utils import (
    initialize_logging,
    get_embedding,
    create_index,
    delete_index,
    has_index,
    upsert_items,
    vector_client_async
)

_logger = logging.getLogger("vector-code-index-put")

def read_code(directory: str) -> List[Document]:
    """Load and process code files from a directory within the 'to_index' folder."""
    loader = GenericLoader.from_filesystem(
        os.path.join(f"./{PROJECT_CODE_DIRECTORY}", directory),
        suffixes=[".ts", ".js", ".mjs", ".jsx", ".tsx"],
        parser=LanguageParser(language=Language.JS),
    )
    docs = loader.load()
    for doc in docs:
        doc.metadata["language"] = doc.metadata.get("language", Language.JS).value

    return RecursiveCharacterTextSplitter.from_language(
        language=Language.JS, 
        chunk_size=SOURCE_CHUNK_SIZE, 
        chunk_overlap=0
    ).split_documents(docs)


async def doc_embeddings(documents: List[Document]) -> List[Item]:
    """Generate embeddings for documents, returning them as a list of Items with unique identifiers."""
    items = []
    source_counts = {}
    tasks = []

    for doc in documents:
        source_path = doc.metadata["source"]
        hashed_path = hashlib.md5(source_path.encode()).hexdigest()
        count = source_counts.setdefault(hashed_path, 0)
        unique_id = f"{hashed_path}_{count:02}"

        task = get_embedding(doc.page_content)
        tasks.append((task, unique_id, doc.metadata))
        source_counts[hashed_path] = count + 1

    embeddings = await asyncio.gather(*[task for task, _, _ in tasks])

    for (task, unique_id, metadata), vector in zip(tasks, embeddings):
        item = Item(vector=vector, id=unique_id, metadata=metadata)
        items.append(item)

    return items


async def read_and_embed(directory: str) -> List[Item]:
    splits = read_code(directory)
    return await doc_embeddings(splits)


async def main(repository_name: str) -> None:
    """Create vector index and upload items in batches

    This function does the following:
    1. Reads source code files in the given repository and embeds them into vectors 
    2. Creates a vector index if one does not already exist.
    3. Batches the items into groups of size 3 and uploads them to the index one batch at a time.
    """
    items = await read_and_embed(repository_name)
    mvi_client = vector_client_async()

    if await has_index(mvi_client, repository_name):
        _logger.debug(f"Deleting existing index {repository_name!r}")
        await delete_index(mvi_client, repository_name)

    num_dimensions = len(items[0].vector)
    _logger.debug(f"Creating index {repository_name!r} with {num_dimensions} dimensions")
    await create_index(mvi_client, repository_name, num_dimensions)

    task_list = []
    batch_size = 3
    for start in range(0, len(items), batch_size):
        end = min(start + batch_size, len(items))
        batch = items[start:end]
        task = upsert_items(mvi_client, repository_name, batch)
        task_list.append(task)

    _logger.debug(f"Uploading {len(task_list)} batches of {batch_size} items to index {repository_name!r}")
    await asyncio.gather(*task_list)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python idx_put.py <directory_name>")
        sys.exit(1)

    initialize_logging()
    directory = sys.argv[1]
    asyncio.run(main(directory))
