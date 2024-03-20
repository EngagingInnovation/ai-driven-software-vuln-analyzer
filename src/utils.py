import asyncio
import os
import colorlog
import logging
from typing import List, Optional
from aiolimiter import AsyncLimiter

from momento import (
    CredentialProvider,
    PreviewVectorIndexClientAsync,
    VectorIndexConfigurations,
)
from momento.config import VectorIndexConfiguration
from momento.logs import TRACE
from momento.requests.vector_index import ALL_METADATA, Item, SimilarityMetric
from momento.responses.vector_index import (
    CreateIndex,
    DeleteIndex,
    ListIndexes,
    Search,
    SearchResponse,
    UpsertItemBatch,
)

from openai import AsyncOpenAI
from config import OPENAI_EMBEDDING_MODEL

_logger = logging.getLogger("vector-code-index-utils")

def initialize_logging() -> None:
    """ Initialize logging with colorized output. """
    debug_mode = os.getenv("DEBUG")
    trace_mode = os.getenv("TRACE")
    if trace_mode == "true":
        log_level = TRACE
    elif debug_mode == "true":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(thin_cyan)s%(name)s%(reset)s %(message)s"
        )
    )
    handler.setLevel(log_level)
    root_logger.addHandler(handler)


# OPENAI
openai_client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
openai_limiter = AsyncLimiter(600, 60)  # 600 requests per 60 seconds, remains within the RPM of the OpenAI usage tier 1

async def get_embedding(text: str, model=OPENAI_EMBEDDING_MODEL, **kwargs) -> List[float]:
    async with openai_limiter:
        text = text.replace("\n", " ")
        response = await openai_client.embeddings.create(input=[text], model=model, **kwargs)
        return response.data[0].embedding


# MOMENTO
# helper functions from Momento
VECTOR_INDEX_CONFIGURATION: VectorIndexConfiguration = (VectorIndexConfigurations.Default.latest())
VECTOR_AUTH_PROVIDER = CredentialProvider.from_environment_variable("MOMENTO_API_KEY")

def vector_client_async() -> PreviewVectorIndexClientAsync:
    return PreviewVectorIndexClientAsync(VECTOR_INDEX_CONFIGURATION, VECTOR_AUTH_PROVIDER)


async def create_index(
    client: PreviewVectorIndexClientAsync,
    index_name: str,
    num_dimensions: int,
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE_SIMILARITY,
) -> None:
    _logger.info(f"Creating index with name {index_name!r}")
    create_index_response = await client.create_index(index_name, num_dimensions, similarity_metric)
    match create_index_response:
        case CreateIndex.Success():
            _logger.info(f"Index with name {index_name!r}  successfully created!")
        case CreateIndex.IndexAlreadyExists():
            _logger.info(f"Index with name {index_name!r} already exists")
        case CreateIndex.Error() as create_index_error:
            _logger.error(f"Error while creating index {create_index_error.message}")
        case _:
            _logger.error("Unreachable")
    _logger.info("")


async def delete_index(client: PreviewVectorIndexClientAsync, index_name: str) -> None:
    _logger.info("Deleting index " + index_name)
    delete_response = await client.delete_index(index_name)

    match delete_response:
        case DeleteIndex.Success():
            _logger.info(f"Index {index_name} deleted successfully!")
        case DeleteIndex.Error() as delete_error:
            _logger.error(f"Failed to delete index {index_name} with error {delete_error.message}")
        case _:
            _logger.error("Unreachable")
    _logger.info("")


async def has_index(client: PreviewVectorIndexClientAsync, index_name: str) -> bool:
    _logger.info("Listing indexes:")
    list_indexes_response = await client.list_indexes()
    match list_indexes_response:
        case ListIndexes.Success() as success:
            for index in success.indexes:
                _logger.info(f"- {index!r}")
                if(index.name == index_name):
                    return True
        case ListIndexes.Error() as list_indexes_error:
            _logger.error(f"Error while listing indexes {list_indexes_error.message}")
            return False
        case _:
            _logger.error("Unreachable")
            return False
    _logger.info("")
    return False


async def upsert_items(client: PreviewVectorIndexClientAsync, index_name: str, items: List) -> None:
    _logger.trace(f"Adding items {items}")
    upsert_response = await client.upsert_item_batch(
        index_name,
        items=items,
    )
    match upsert_response:
        case UpsertItemBatch.Success():
            _logger.info("Successfully added items")
        case UpsertItemBatch.Error() as upsert_error:
            _logger.error(f"Error while adding items to index {index_name!r}: {upsert_error.message}")
        case _:
            _logger.error("Unreachable")


async def search(client: PreviewVectorIndexClientAsync, index_name: str, query_vector: List[float], top_k: int) -> SearchResponse:
    _logger.debug(f"Searching index {index_name} and top {top_k} elements")
    search_response = await client.search(index_name, query_vector=query_vector, top_k=top_k, metadata_fields=ALL_METADATA)
    match search_response:
        case Search.Success() as success:
            _logger.debug(f"Search succeeded with {len(success.hits)} matches:")
            #_logger.info(success.hits)
            return success
        case Search.Error() as search_error:
            _logger.error(f"Error while searching on index {index_name}: {search_error.message}")
        case _:
            _logger.error("Unreachable")
    _logger.info("")
    return search_response
