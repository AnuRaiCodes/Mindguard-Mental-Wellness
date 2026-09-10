"""
rag/pipeline.py — Retrieval-Augmented Generation pipeline using FAISS
"""
import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Lazy imports — gracefully degrade if libraries unavailable
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available — RAG will use fallback mode")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("faiss-cpu not available — RAG will use keyword fallback")


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.
    Loads knowledge-base documents, creates embeddings, and retrieves
    relevant context for each user query.
    """

    def __init__(self, knowledge_base_dir: str, index_path: str, model_name: str = "all-MiniLM-L6-v2", top_k: int = 4):
        self.knowledge_base_dir = knowledge_base_dir
        self.index_path = index_path
        self.model_name = model_name
        self.top_k = top_k

        self.chunks: List[str] = []
        self.chunk_sources: List[str] = []
        self.model = None
        self.index = None
        self._initialized = False

    def initialize(self):
        """Build or load the FAISS index."""
        if self._initialized:
            return

        docs = self._load_documents()
        if not docs:
            logger.error("No knowledge-base documents found — RAG disabled")
            return

        self.chunks, self.chunk_sources = self._chunk_documents(docs)

        if SENTENCE_TRANSFORMERS_AVAILABLE and FAISS_AVAILABLE:
            self._build_or_load_index()
        else:
            logger.warning("Using keyword search fallback for RAG")

        self._initialized = True
        logger.info(f"RAG pipeline initialized with {len(self.chunks)} chunks")

    def _load_documents(self) -> List[Tuple[str, str]]:
        """Load all .txt files from the knowledge base directory."""
        docs = []
        kb_path = Path(self.knowledge_base_dir)
        if not kb_path.exists():
            logger.warning(f"Knowledge base directory not found: {kb_path}")
            return docs

        for txt_file in sorted(kb_path.glob("*.txt")):
            try:
                content = txt_file.read_text(encoding="utf-8")
                docs.append((txt_file.name, content))
                logger.info(f"Loaded: {txt_file.name}")
            except Exception as e:
                logger.error(f"Error loading {txt_file}: {e}")

        return docs

    def _chunk_documents(self, docs: List[Tuple[str, str]], chunk_size: int = 400, overlap: int = 50) -> Tuple[List[str], List[str]]:
        """Split documents into overlapping chunks."""
        chunks = []
        sources = []

        for source_name, content in docs:
            # Split by paragraphs first
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            current_chunk = ""
            current_words = 0

            for para in paragraphs:
                para_words = len(para.split())
                if current_words + para_words > chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    sources.append(source_name)
                    # Keep last overlap words
                    words = current_chunk.split()
                    current_chunk = " ".join(words[-overlap:]) + "\n\n" + para
                    current_words = overlap + para_words
                else:
                    current_chunk = (current_chunk + "\n\n" + para).strip()
                    current_words += para_words

            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                sources.append(source_name)

        return chunks, sources

    def _build_or_load_index(self):
        """Build FAISS index from chunks or load a cached version."""
        index_file = Path(self.index_path + ".faiss")
        meta_file = Path(self.index_path + ".meta.json")

        # Load existing index if chunk count matches
        if index_file.exists() and meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text())
                if meta.get("chunk_count") == len(self.chunks):
                    self.model = SentenceTransformer(self.model_name)
                    self.index = faiss.read_index(str(index_file))
                    logger.info("Loaded cached FAISS index")
                    return
            except Exception as e:
                logger.warning(f"Could not load cached index: {e}")

        # Build new index
        logger.info("Building FAISS index…")
        self.model = SentenceTransformer(self.model_name)
        embeddings = self.model.encode(self.chunks, show_progress_bar=False)
        embeddings = embeddings.astype(np.float32)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        # Save
        os.makedirs(os.path.dirname(self.index_path) if os.path.dirname(self.index_path) else ".", exist_ok=True)
        faiss.write_index(self.index, str(index_file))
        meta_file.write_text(json.dumps({"chunk_count": len(self.chunks), "model": self.model_name}))
        logger.info(f"FAISS index built and saved ({len(self.chunks)} chunks)")

    def retrieve(self, query: str) -> str:
        """Retrieve relevant context for a query."""
        if not self._initialized:
            self.initialize()

        if not self.chunks:
            return ""

        if SENTENCE_TRANSFORMERS_AVAILABLE and FAISS_AVAILABLE and self.model and self.index:
            return self._semantic_retrieve(query)
        else:
            return self._keyword_retrieve(query)

    def _semantic_retrieve(self, query: str) -> str:
        """Semantic search using FAISS."""
        query_vec = self.model.encode([query]).astype(np.float32)
        k = min(self.top_k, len(self.chunks))
        distances, indices = self.index.search(query_vec, k)

        results = []
        for idx in indices[0]:
            if idx >= 0 and idx < len(self.chunks):
                source = self.chunk_sources[idx]
                results.append(f"[Source: {source}]\n{self.chunks[idx]}")

        return "\n\n---\n\n".join(results) if results else ""

    def _keyword_retrieve(self, query: str) -> str:
        """Simple keyword-based fallback retrieval."""
        query_words = set(query.lower().split())
        stop_words = {"a", "an", "the", "is", "are", "was", "were", "i", "me", "my",
                      "do", "does", "can", "what", "how", "why", "when", "where"}
        query_words -= stop_words

        scored = []
        for i, chunk in enumerate(self.chunks):
            chunk_lower = chunk.lower()
            score = sum(1 for w in query_words if w in chunk_lower)
            if score > 0:
                scored.append((score, i))

        scored.sort(reverse=True)
        top_indices = [i for _, i in scored[:self.top_k]]

        results = []
        for idx in top_indices:
            source = self.chunk_sources[idx]
            results.append(f"[Source: {source}]\n{self.chunks[idx]}")

        return "\n\n---\n\n".join(results) if results else ""


# Singleton instance (initialized lazily)
_rag_pipeline: RAGPipeline | None = None


def get_rag_pipeline(app=None) -> RAGPipeline:
    """Get or create the singleton RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        if app:
            kb_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), app.config["KNOWLEDGE_BASE_DIR"])
            index_path = app.config["FAISS_INDEX_PATH"]
            model_name = app.config["EMBEDDING_MODEL"]
            top_k = app.config["RAG_TOP_K"]
        else:
            kb_dir = "knowledge_base"
            index_path = "instance/faiss_index"
            model_name = "all-MiniLM-L6-v2"
            top_k = 4

        _rag_pipeline = RAGPipeline(kb_dir, index_path, model_name, top_k)
        _rag_pipeline.initialize()

    return _rag_pipeline
