from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.retrievers import EnsembleRetriever, BM25Retriever
from langchain_community.document_loaders import (
    TextLoader,
    PDFMinerLoader,
    UnstructuredWordDocumentLoader,
    CSVLoader,
)
from pathlib import Path

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

BASE_PATH = Path("data/knowledge_base")


def load_all_documents_from_folder(folder_path: Path):
    all_docs = []
    for file_path in folder_path.glob("*"):
        if not file_path.is_file():
            continue

        try:
            if file_path.suffix == ".txt":
                loader = TextLoader(str(file_path), encoding="utf-8")
            elif file_path.suffix == ".pdf":
                loader = PDFMinerLoader(str(file_path))
            elif file_path.suffix == ".docx":
                loader = UnstructuredWordDocumentLoader(str(file_path))
            elif file_path.suffix == ".csv":
                loader = CSVLoader(str(file_path),encoding="utf-8")
            else:
                continue  # Skip unsupported files

            docs = loader.load()
            all_docs.extend(docs)
        except Exception as e:
            print(f"❌ Error loading {file_path.name}: {e}")

    return all_docs


def build_retriever(k: int = 2):
    documents = load_all_documents_from_folder(BASE_PATH)
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_documents(documents)

    # Semantic Retriever (FAISS)
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]
    faiss_vectorstore = FAISS.from_texts(texts=texts, embedding=embedding, metadatas=metadatas)
    faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": k})

    # Keyword Retriever (BM25)
    bm25_retriever = BM25Retriever.from_documents(docs)
    bm25_retriever.k = k

    # Combine both using EnsembleRetriever
    ensemble = EnsembleRetriever(
        retrievers=[faiss_retriever, bm25_retriever],
    )
    
    return ensemble

def get_retriever(k: int = 2):
    return build_retriever(k)


