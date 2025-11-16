from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.utils.file_loader import clone_repo
from app.ingestion_pipeline import store_data
from app.retriever_pipeline import ask_question, resetMemory
from app.utils.file_ext import list_files, read_file, generate_tree
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Codebase Investigator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RepoUrlReq(BaseModel):
    url : str

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    source: str

class AskCode(BaseModel):
    dir: str

current_source = None

@app.post("/api/clone_repos")
def clone_repos(req: RepoUrlReq):
    try:
        clone_repo(req.url)
        store_data()
        return {"message": "The repo was cloned successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cloning repo: {str(e)}")


@app.post("/api/chat", response_model=AskResponse)
def llm_chat(req: AskRequest):
    global current_source
    try:
        result = ask_question(req.question)
        current_source = result["context"][0].metadata["source"]
        return {
            "answer": result["answer"],
            "source": current_source
        }
    except IndexError:
        raise HTTPException(status_code=404, detail="No context found for the question")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")



@app.get("/api/source")
def get_source():
    return {"source": current_source}


@app.get("/api/list_files")
def get_list_files():
    try:
        files = list_files("data/raw_repo")
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")



@app.post("/api/show_code")
def show_code(req: AskCode):
    try:
        text = read_file(req.dir)
        return {"fileText": text}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")



@app.get("/api/tree_structure")
def tree_structure():
    tree = generate_tree("data/raw_repo", lines=["project"])
    return {"tree": tree}


@app.get("/api/reset_memory")
def reset_memory():
    resetMemory()
    return {"message": "Memory has been reset"}