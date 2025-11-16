from git import Repo, GitCommandError
from langchain_community.document_loaders import TextLoader, DirectoryLoader
import os
import shutil

def clone_repo(repo_url, fdir="data/raw_repo"):
    try:
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        Repo.clone_from(repo_url, fdir)
        print(f"Repository cloned into {fdir}")

    except GitCommandError as e:
        if "already exists" in str(e):
            print(f"Repository already exists in '{fdir}'. Removing and recloning...")
            try:
                shutil.rmtree(fdir)
                Repo.clone_from(repo_url, fdir)
                print(f"Repository re-cloned into: {fdir}")
            except Exception as inner_e:
                print(f"Failed to re-clone: {inner_e}")
        else:
            print(f"Git error occurred: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

def load_code(fdir="data/raw_repo"):
    loader = DirectoryLoader(
        fdir,
        glob=["**/*.py", "**/*.md", "**/*.js", "**/*.java"],    
        loader_cls=TextLoader,
        show_progress=True
    )
    
    documents = loader.load()
    print("doc has been loaded")
    return documents

