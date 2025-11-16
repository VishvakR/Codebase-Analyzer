from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from app.utils.file_loader import load_code
import os
import shutil

docs = load_code()

def store_data(persist_dir="data/chroma_vector_db"):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\nclass ", "\ndef ", "\n\n", "\n", " "]
    )

    chunks = []
    for d in docs:
        chunks.extend(splitter.split_documents([d]))

    
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    ids = [
        f"{os.path.basename(c.metadata['source'])}_chunk_{i}"
        for i, c in enumerate(chunks)
    ]

    vector_store = Chroma(
        collection_name="collections",
        embedding_function=embedding,
        persist_directory="data/chroma_vector_db",
    )
    if os.path.exists("data/chroma_vector_db"):
        vector_store.delete_collection()
        vector_store = Chroma(
            collection_name="collections",
            embedding_function=embedding,
            persist_directory="data/chroma_vector_db",
        )
    vector_store.add_documents(chunks, ids=ids)

    print("Vector database created with mixed file types.")
