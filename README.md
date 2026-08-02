# 🚀 OpenWorker Universal Engine

> An AI-powered autonomous software engineering platform that analyzes repositories, understands project architecture, generates implementation plans, performs intelligent code modifications, and exports production-ready projects using Large Language Models (LLMs).

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)
![License](https://img.shields.io/badge/License-MIT-orange.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

---

# 📖 Table of Contents

- Overview
- Problem Statement
- Solution
- Features
- System Architecture
- Workflow
- Project Structure
- Technologies Used
- Installation
- Configuration
- Running the Project
- API Endpoints
- AI Agents
- Repository Analyzer
- Tool Registry
- Logging
- Export System
- Future Improvements
- Contributing
- License

---

# 📌 Overview

OpenWorker Universal Engine is an autonomous AI software engineering platform that assists developers throughout the software development lifecycle.

Instead of manually exploring large codebases, understanding project architecture, planning implementations, and modifying source code, OpenWorker performs these tasks automatically using Large Language Models (LLMs).

The platform can analyze uploaded repositories, detect programming languages and frameworks, generate implementation strategies, edit code intelligently, execute development tools, and export the completed project.

It is designed to improve developer productivity while maintaining an organized, modular, and scalable workflow.

---

# ❗ Problem Statement

Modern software projects often contain thousands of files and complex architectures.

Developers spend significant time:

- Understanding project structure
- Identifying dependencies
- Reading documentation
- Planning implementations
- Modifying existing code
- Updating documentation

These repetitive tasks reduce development efficiency and increase onboarding time.

OpenWorker automates these processes using AI-driven software engineering.

---

# 💡 Solution

OpenWorker provides an autonomous workflow that:

1. Accepts an existing project.
2. Creates an isolated workspace.
3. Analyzes repository structure.
4. Detects technologies used.
5. Generates an implementation strategy.
6. Uses AI to perform development tasks.
7. Executes tools when required.
8. Generates documentation.
9. Exports the completed project.

This enables developers to focus on solving business problems rather than repetitive engineering tasks.

---

# ✨ Features

## Repository Analysis

- Upload ZIP projects
- Import Git repositories
- Detect programming languages
- Detect frameworks
- Detect package managers
- Detect build systems
- Analyze repository statistics

---

## AI Planning

- Understand user requirements
- Analyze repository architecture
- Generate implementation strategy
- Produce PLAN.md automatically

---

## Autonomous Development

- Read project files
- Create new files
- Modify existing files
- Refactor code
- Generate documentation
- Execute development tools

---

## Workspace Management

- Session-based execution
- Isolated workspaces
- Automatic cleanup
- Export completed projects

---

## Monitoring

- Real-time logs
- Execution history
- Session tracking
- Error reporting

---

# 🏗 System Architecture

```
                User
                  │
                  ▼
          FastAPI REST API
                  │
                  ▼
         Session Manager
                  │
                  ▼
       Repository Analyzer
                  │
                  ▼
          Architect Agent
                  │
                  ▼
            PLAN.md
                  │
                  ▼
           Worker Agent
                  │
                  ▼
          Tool Registry
                  │
                  ▼
      Workspace Execution
                  │
                  ▼
        Project Export
```

---

# 🔄 Workflow

### Step 1

Upload a project ZIP or Git repository.

↓

### Step 2

Create a unique workspace.

↓

### Step 3

Extract project files.

↓

### Step 4

Analyze repository.

↓

### Step 5

Identify

- Languages
- Frameworks
- Dependencies
- Build tools

↓

### Step 6

Architect Agent generates a development plan.

↓

### Step 7

Worker Agent executes implementation.

↓

### Step 8

Tools modify project files.

↓

### Step 9

Generate documentation.

↓

### Step 10

Export completed project.

---

# 📁 Project Structure

```
backend/
│
├── api/
├── core/
├── repository/
├── llm/
├── agents/
├── tools/
├── workspace/
├── services/
├── utils/
│
├── main.py
│
exports/
logs/
workspaces/

requirements.txt
README.md
```

---

# ⚙ Technologies Used

## Backend

- Python
- FastAPI
- Uvicorn

## AI

- Ollama
- Qwen3

## Validation

- Pydantic

## Communication

- REST API
- Server-Sent Events

## Utilities

- HTTPX
- Requests

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/yourusername/openworker.git
```

Move into the project

```bash
cd openworker
```

Create virtual environment

```bash
python -m venv venv
```

Activate environment

Windows

```bash
venv\Scripts\activate
```

Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶ Running the Server

```bash
uvicorn main:app --reload
```

Server starts at

```
http://localhost:8000
```

Swagger Documentation

```
http://localhost:8000/docs
```

---

# 📡 API Endpoints

## Health Check

```
GET /api/v1/health
```

Returns server status.

---

## Upload Repository

```
POST /api/v1/sessions/upload
```

Creates a new workspace and starts repository analysis.

---

## Session Logs

```
GET /api/v1/sessions/{session_id}/stream
```

Streams live execution logs.

---

## Export Project

Returns the completed project archive.

---

# 🤖 AI Agents

## Architect Agent

Responsibilities

- Understand project goals
- Analyze architecture
- Plan implementation
- Generate PLAN.md

Outputs

- Development strategy
- Required modules
- Architecture notes

---

## Worker Agent

Responsibilities

- Read source files
- Modify code
- Create files
- Execute tools
- Validate changes

Outputs

- Updated source code
- Documentation
- README_CHANGES.md

---

# 🔍 Repository Analyzer

The analyzer scans the uploaded project and extracts:

- Programming languages
- Frameworks
- Package managers
- Build systems
- Repository statistics
- Directory hierarchy
- Dependencies
- File relationships

These insights help the AI understand the project before making changes.

---

# 🛠 Tool Registry

The Worker Agent interacts with the project through controlled development tools.

Supported tools include:

- File Reader
- File Writer
- Search
- Replace
- Terminal Execution
- Documentation Generator

Using tools instead of unrestricted file access improves reliability and safety.

---

# 📄 Logging

Every important action is recorded.

Examples:

- Repository uploaded
- Repository analyzed
- Plan generated
- Tool executed
- File modified
- Build completed
- Export created

Logs are available in real time for debugging and monitoring.

---

# 📦 Export System

After successful execution the system automatically packages:

- Updated source code
- Generated documentation
- PLAN.md
- README_CHANGES.md

The project can then be downloaded as a ZIP archive.

---

# 🎯 Advantages

- Faster project onboarding
- Automated repository understanding
- Reduced manual coding effort
- Intelligent code generation
- Organized workflow
- Modular architecture
- Easy integration
- Scalable design

---

# ⚠ Limitations

- AI output depends on model quality.
- Large repositories require more processing time.
- Human review is recommended before deployment.
- Complex architectural changes may require manual intervention.

---

# 🔮 Future Enhancements

- GitHub Pull Request integration
- Docker deployment
- Kubernetes support
- Multi-agent collaboration
- Unit test generation
- CI/CD integration
- Security vulnerability scanning
- Static code analysis
- Cloud deployment
- Multi-model support (OpenAI, Claude, Gemini)

---

# 🤝 Contributing

Contributions are welcome!

To contribute:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Commit your code
5. Push to your branch
6. Open a Pull Request

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**OpenWorker Universal Engine**

An AI-powered autonomous software engineering platform designed to simplify repository analysis, intelligent code generation, and automated software development workflows.

👨‍💻 About Me
Hi, I'm Shivam Solanki
---

## ⭐ If you find this project useful, don't forget to star the repository!
