import os
from pathlib import Path

from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings


def load_epub_text(epub_path):
    """
    Load text content from an EPUB file.
    
    Args:
        epub_path (str): Path to the EPUB file.
        
    Returns:
        str: Combined text content from all chapters in the EPUB.
    """
    book = epub.read_epub(epub_path)
    text_content = []
    
    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.content, 'html.parser')
            text_content.append(soup.get_text())
    
    return "\n".join(text_content)


def create_vector_index(epub_path, index_dir="indexes/cocktail_index"):
    """
    Create a FAISS vector index from an EPUB file.

    Args:
        epub_path (str): Path to the EPUB file.
        index_dir (str): Directory to save the FAISS index.
    """
    os.makedirs(index_dir, exist_ok=True)
    raw_text = load_epub_text(epub_path)

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = splitter.create_documents([raw_text])

    embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(documents, embedder)
    db.save_local(index_dir)


def load_vector_index(index_dir="indexes/cocktail_index"):
    """
    Load an existing FAISS vector index.

    Args:
        index_dir (str): Directory where the FAISS index is stored.

    Returns:
        FAISS: Loaded FAISS vector store object
    """
    embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.load_local(
        str(Path(index_dir)),
        embedder,
        allow_dangerous_deserialization=True
    )
