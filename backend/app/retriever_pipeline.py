from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

db = Chroma(
    persist_directory="data/chroma_vector_db",
    embedding_function=embedding
)
conversation_memory = []
MAX_MEMORY = 5

def get_history():
    if not conversation_memory:
        return "None"
    return "\n".join([f"Q: {q}\nA: {a}" for q, a in conversation_memory])


retriever = db.as_retriever(search_kwargs={"k": 3})

llm = OllamaLLM(model="llama3.1:8b")

prompt = ChatPromptTemplate.from_template("""
You are a helpful coding assistant that can analyze codebases and answer developer questions.

Here is the conversation so far:
{history}

Use the context below to answer the current question accurately.

Context:
{context}

Current Question:
{input}

Answer:
""")

combine_docs_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

def resetMemory():
    conversation_memory.clear()
    print("memory has reset")

def ask_question(ques: str):
    history = get_history()
    response = retrieval_chain.invoke({"input": ques, "history": history})
    conversation_memory.append((ques, response["answer"]))
    if len(conversation_memory) > MAX_MEMORY:
        conversation_memory.pop(0)
    return response

