from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

BASE_PATH = Path("data/knowledge_base")
FILES = ["sample.txt", "uploaded_content.txt"]

def load_all_documents():
    all_docs = []
    for file in FILES:
        file_path = BASE_PATH / file
        if file_path.exists():
            loader = TextLoader(str(file_path), encoding="utf-8")
            docs = loader.load()
            all_docs.extend(docs)
    return all_docs

def build_retriever(k: int = 3):
    documents = load_all_documents()
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    docs = splitter.split_documents(documents)
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]
    vectorstore = FAISS.from_texts(texts=texts, embedding=embedding, metadatas=metadatas)
    return vectorstore.as_retriever(search_kwargs={"k": k})

def get_retriever(k: int = 3):
    return build_retriever(k)


