import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
from rag_utils import load_epub_text, create_vector_index, load_vector_index


TEST_EPUB_PATH = Path("tests/test_data.epub")
TEST_INDEX_PATH = Path("tests/test_vector_index")


def test_load_epub_text():
    assert TEST_EPUB_PATH.exists(), f"Test EPUB file {TEST_EPUB_PATH} does not exist."
    content = load_epub_text(TEST_EPUB_PATH)
    assert isinstance(content, str)
    assert len(content) > 0, "Loaded content should not be empty."


def test_create_vector_index():
    if (TEST_INDEX_PATH / "index.faiss").exists():
        (TEST_INDEX_PATH / "index.faiss").unlink()
    if (TEST_INDEX_PATH / "index.pkl").exists():
        (TEST_INDEX_PATH / "index.pkl").unlink()

    create_vector_index(str(TEST_EPUB_PATH), index_dir=str(TEST_INDEX_PATH))

    assert (TEST_INDEX_PATH / "index.faiss").exists(), "index.faiss not found."
    assert (TEST_INDEX_PATH / "index.pkl").exists(), "index.pkl not found."


def test_load_vector_index():
    if not (TEST_INDEX_PATH / "index.faiss").exists():
        create_vector_index(str(TEST_EPUB_PATH), index_dir=str(TEST_INDEX_PATH))

    vector_index = load_vector_index(index_dir=str(TEST_INDEX_PATH))
    assert hasattr(vector_index, "similarity_search")

    results = vector_index.similarity_search("martini", k=1)
    assert len(results) > 0, "No results returned from similarity search."
