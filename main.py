import os
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
import ctags
from typing import List
import shutil

app = FastAPI(title="CodeGrok API", description="Source code search and generation engine")

# Configuration
SRC_ROOT = os.getenv("SRC_ROOT", "/codegrok/src")
INDEX_DIR = os.getenv("INDEX_DIR", "/codegrok/index")
CTAGS_PATH = shutil.which("ctags") or "universal-ctags"

# Whoosh schema for search
schema = Schema(
    path=ID(stored=True, unique=True),
    content=TEXT(stored=True),
    language=TEXT(stored=True)
)

# Initialize index
if not os.path.exists(INDEX_DIR):
    os.makedirs(INDEX_DIR)
    create_in(INDEX_DIR, schema)

class SearchQuery(BaseModel):
    query: str
    limit: int = 10

class ProjectGenerate(BaseModel):
    project_type: str  # e.g., "react-flask", "vue-express"
    name: str

@app.get("/")
async def root():
    return {"message": "Welcome to CodeGrok! Use /search or /generate to get started."}

@app.post("/search")
async def search_code(query: SearchQuery):
    """Search code files for a query string."""
    try:
        ix = open_dir(INDEX_DIR)
        with ix.searcher() as searcher:
            q = QueryParser("content", ix.schema).parse(query.query)
            results = searcher.search(q, limit=query.limit)
            return [{"path": hit["path"], "language": hit["language"], "snippet": hit.highlights("content")} for hit in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/index")
async def index_project():
    """Index all files in SRC_ROOT."""
    try:
        ix = create_in(INDEX_DIR, schema)
        writer = ix.writer()
        
        for root, _, files in os.walk(SRC_ROOT):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                language = {
                    ".py": "python",
                    ".js": "javascript",
                    ".ts": "typescript",
                    ".java": "java",
                    ".html": "html",
                    ".css": "css",
                    ".sql": "sql"
                }.get(ext, "unknown")
                
                if language != "unknown":
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        writer.add_document(
                            path=file_path,
                            content=content,
                            language=language
                        )
        writer.commit()
        return {"message": f"Indexed {SRC_ROOT} successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@app.post("/crossref")
async def cross_reference(symbol: str):
    """Find references to a symbol using ctags."""
    try:
        cmd = [CTAGS_PATH, "-R", "--fields=+n", "--output-format=json", SRC_ROOT]
        result = subprocess.run(cmd, capture_output=True, text=True)
        tags = [line for line in result.stdout.splitlines() if symbol in line]
        return {"references": tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-reference failed: {str(e)}")

@app.post("/generate")
async def generate_project(project: ProjectGenerate):
    """Generate a new project (frontend + backend)."""
    templates = {
        "react-flask": {
            "frontend": {
                "path": "frontend",
                "files": {
                    "src/App.js": """
import React from 'react';
function App() {
  return <div>Welcome to {project.name}!</div>;
}
export default App;
"""
                }
            },
            "backend": {
                "path": "backend",
                "files": {
                    "app.py": """
from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello from {project.name}!'
if __name__ == '__main__':
    app.run(debug=True)
"""
                }
            }
        }
    }
    
    template = templates.get(project.project_type)
    if not template:
        raise HTTPException(status_code=400, detail="Unsupported project type")
    
    project_dir = os.path.normpath(os.path.join(SRC_ROOT, project.name))
    if not project_dir.startswith(SRC_ROOT):
        raise HTTPException(status_code=400, detail="Invalid project name")
    os.makedirs(project_dir, exist_ok=True)
    
    for component in [template["frontend"], template["backend"]]:
        comp_dir = os.path.normpath(os.path.join(project_dir, component["path"]))
        if not comp_dir.startswith(project_dir):
            raise HTTPException(status_code=400, detail="Invalid component path")
        os.makedirs(comp_dir, exist_ok=True)
        for file_path, content in component["files"].items():
            sanitized_file_path = os.path.normpath(file_path)
            if not sanitized_file_path or ".." in sanitized_file_path or sanitized_file_path.startswith("/"):
                raise HTTPException(status_code=400, detail="Invalid file path")
            full_file_path = os.path.join(comp_dir, sanitized_file_path)
            with open(full_file_path, "w") as f:
                f.write(content.format(project=project))
    
    return {"message": f"Generated {project.name} at {project_dir}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)