# CodeGrok

**CodeGrok** is a lightweight, extensible source code search and cross-reference engine designed for developers. Inspired by OpenGrok, CodeGrok focuses on simplifying code navigation, search, and generation of full-stack projects (frontend to endpoint) with a modern, user-friendly interface and a permissive MIT license.

## Features
- **Fast Code Search**: Full-text search across codebases using Whoosh, supporting languages like JavaScript, Python, Java, HTML, CSS, and SQL.
- **Cross-Referencing**: Navigate code with go-to-definition and find-references using Universal Ctags.
- **Code Generation**: Generate boilerplate for full-stack projects (e.g., React + Flask, Vue + Express) directly from the UI or API.
- **Modern UI**: Responsive React-based interface with Tailwind CSS for seamless code browsing and project creation.
- **SCM Integration**: Index Git repositories with planned support for GitHub webhooks for real-time updates.
- **Permissive License**: MIT license for unrestricted use and contributions.
- **Easy Deployment**: Run locally or via Docker with minimal setup.

## Architecture
- **Backend**: Python with FastAPI for a fast, RESTful API.
- **Frontend**: React with Tailwind CSS for a modern, responsive UI.
- **Search**: Whoosh for full-text search and Universal Ctags for code navigation.
- **Deployment**: Docker for one-command setup.
- **Storage**: SQLite for configuration; file-based indexing for simplicity.

## Getting Started

### Prerequisites
- Docker (recommended for easy deployment).
- Python 3.9+ (if running without Docker).
- Git (for cloning repositories).
- Universal Ctags (`ctags`) for code navigation.

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/codegrok.git
   cd codegrok
   ```

2. **Directory Structure**:
   Create the following structure:
   ```
   /codegrok
   ├── src/               # Source code repositories
   ├── index/             # Search index
   ├── main.py            # FastAPI backend
   ├── index.html         # React frontend
   ├── Dockerfile         # Docker configuration
   ├── requirements.txt   # Python dependencies
   ├── LICENSE            # MIT license
   └── README.md          # This file
   ```

3. **Run with Docker** (Recommended):
   ```bash
   docker build -t codegrok .
   docker run -d -p 8000:8000 -v $(pwd)/src:/codegrok/src -v $(pwd)/index:/codegrok/index codegrok
   ```
   Access CodeGrok at `http://localhost:8000`.

4. **Run Locally** (Without Docker):
   ```bash
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
   Ensure `universal-ctags` is installed (`apt-get install universal-ctags` on Ubuntu).

### Usage

1. **Index a Repository**:
   - Clone a repository into `/codegrok/src`:
     ```bash
     git clone https://github.com/user/repo /codegrok/src/repo
     ```
   - Index the repository:
     ```bash
     curl -X POST http://localhost:8000/index
     ```

2. **Search Code**:
   - Via UI: Open `http://localhost:8000`, enter a query (e.g., `function`), and view results.
   - Via API:
     ```bash
     curl -X POST http://localhost:8000/search -d '{"query": "function", "limit": 5}' -H "Content-Type: application/json"
     ```

3. **Cross-Reference Symbols**:
   - Find references to a symbol (e.g., a function name):
     ```bash
     curl -X POST http://localhost:8000/crossref -d '{"symbol": "myFunction"}' -H "Content-Type: application/json"
     ```

4. **Generate a Project**:
   - Via UI: Select a project type (e.g., React + Flask), enter a name, and click "Generate".
   - Via API:
     ```bash
     curl -X POST http://localhost:8000/generate -d '{"project_type": "react-flask", "name": "myapp"}' -H "Content-Type: application/json"
     ```
   - Generated projects are saved in `/codegrok/src/myapp`.

### Supported Project Types
- `react-flask`: React frontend + Flask backend.
- `vue-express`: Vue.js frontend + Express backend (more to be added).

### API Endpoints
| Endpoint         | Method | Description                       | Payload Example                                      |
|------------------|--------|-----------------------------------|-----------------------------------------------------|
| `/`              | GET    | Health check                     | -                                                   |
| `/search`        | POST   | Search code                      | `{"query": "function", "limit": 5}`                 |
| `/index`         | POST   | Index source code                | -                                                   |
| `/crossref`      | POST   | Cross-reference a symbol         | `{"symbol": "myFunction"}`                          |
| `/generate`      | POST   | Generate a new project           | `{"project_type": "react-flask", "name": "myapp"}`  |

## Contributing
We welcome contributions! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Commit changes (`git commit -m "Add my