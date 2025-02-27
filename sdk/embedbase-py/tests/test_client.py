# pylint: disable=missing-function-docstring

from typing import List, Union

import numpy as np
import pytest
from embedbase import get_app
from embedbase.database.memory_db import MemoryDatabase
from embedbase.embedding.base import Embedder

from embedbase_client.client import EmbedbaseClient, SearchResult


# pylint: disable=missing-docstring
class FakeEmbedder(Embedder):
    def __init__(self, dimensions: int = 384, **kwargs):
        super().__init__(**kwargs)
        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        """
        Return the dimensions of the embeddings
        :return: dimensions of the embeddings
        """
        return self._dimensions

    def is_too_big(self, text: str) -> bool:
        """
        Check if text is too big to be embedded,
        delegating the splitting UX to the caller
        :param text: text to check
        :return: True if text is too big, False otherwise
        """
        return len(text) > 1000

    async def embed(self, data: Union[List[str], str]) -> List[List[float]]:
        """
        Embed a list of texts
        :param texts: list of texts
        :return: list of embeddings
        """
        # random numpy array
        return np.random.rand(len(data), self._dimensions).tolist()


def run_app():
    return get_app().use_db(MemoryDatabase()).use_embedder(FakeEmbedder()).run()


app = run_app()

# Use a local instance of the API with the fake embedder
base_url = "http://localhost:8000"
client = EmbedbaseClient(embedbase_url=base_url, fastapi_app=app)

# Dataset to be used in tests
test_dataset = "test_dataset"

ds = client.dataset(test_dataset)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    yield

    # Teardown - clear the test dataset
    ds.clear()


def test_add_single_document():
    document = "This is a test document."
    metadata = {"key": "value"}

    result = ds.add(document, metadata)

    assert result["status"] == "success"
    assert isinstance(result["id"], str)


def test_batch_add_documents():
    documents = [
        {"data": "Document 1", "metadata": {"key": "value1"}},
        {"data": "Document 2", "metadata": {"key": "value2"}},
    ]

    results = ds.batch_add(documents)

    assert len(results) == len(documents)
    for result in results:
        assert result["status"] == "success"
        assert isinstance(result["id"], str)


def test_search_documents():
    # Add some documents to the dataset
    documents = [
        {"data": "Document 1", "metadata": {"key": "value1"}},
        {"data": "Document 2", "metadata": {"key": "value2"}},
    ]
    ds.batch_add(documents)

    # Perform a search
    query = "Document"
    results = ds.search(query)

    # Check that the results are SearchResult instances
    assert len(results) > 0
    for result in results:
        assert isinstance(result, SearchResult)

    # Check that the results contain the expected documents
    document_datas = [result.data for result in results]
    for doc in documents:
        assert doc["data"] in document_datas
