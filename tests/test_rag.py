"""
tests/test_rag.py — Tests for the RAG pipeline
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tempfile
import pytest
from rag.pipeline import RAGPipeline


@pytest.fixture
def rag_pipeline(tmp_path):
    # Create a mini knowledge base
    kb = tmp_path / "kb"
    kb.mkdir()
    (kb / "test.txt").write_text(
        "Stress is a natural response. Deep breathing helps reduce stress.\n\n"
        "Anxiety involves excessive worry. CBT is an effective treatment for anxiety.\n\n"
        "Depression causes persistent sadness. Therapy and medication can help."
    )
    index_dir = tmp_path / "index"
    index_dir.mkdir()
    pipeline = RAGPipeline(str(kb), str(index_dir / "faiss"), top_k=2)
    pipeline.initialize()
    return pipeline


def test_pipeline_initializes(rag_pipeline):
    assert rag_pipeline._initialized is True
    assert len(rag_pipeline.chunks) > 0


def test_retrieve_returns_string(rag_pipeline):
    result = rag_pipeline.retrieve("what is stress")
    assert isinstance(result, str)


def test_retrieve_relevant_content(rag_pipeline):
    result = rag_pipeline.retrieve("anxiety treatment")
    # Should find something about anxiety or CBT
    assert len(result) > 0


def test_retrieve_empty_query(rag_pipeline):
    result = rag_pipeline.retrieve("")
    assert isinstance(result, str)


def test_chunk_count(rag_pipeline):
    assert len(rag_pipeline.chunks) >= 1
