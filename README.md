# ShopFlow AI — AI-Powered Customer Support Intelligence

ShopFlow AI is a local AI-powered customer support application that classifies customer messages, retrieves order information, routes cases requiring human attention, and evaluates classification performance.

Built with **Python, FastAPI, React, Vite, SQLite, Ollama, and n8n**, the project demonstrates how AI classification can be combined with backend APIs, workflow automation, analytics, and human-in-the-loop review.

## Features

### 1. AI-Powered Message Classification
- Uses the local `qwen2.5:3b` language model through Ollama.
- Classifies customer messages into intents such as delivery, delayed delivery, refund, damaged item, cancellation, and other.
- Assigns urgency levels: low, medium, or high.
- Identifies cases that require human review.

### 2. Order Lookup
- Retrieves order details using an order ID.
- Displays product information, customer email, order status, payment status, amount, order date, and expected delivery.
- Uses a SQLite database for order records.

### 3. Human Review Queue
- Stores cases flagged for human review.
- Displays the customer message, predicted intent, urgency, and case status.
- Supports filtering by pending, reviewed, and all cases.
- Allows a reviewer to mark a case as reviewed.

### 4. Analytics Dashboard
- Displays total, pending, reviewed, and high-urgency cases.
- Calculates the review completion rate.
- Visualizes intent distribution and review status using charts.
- Displays an intent summary table.

### 5. AI Evaluation Dashboard
- Loads saved evaluation reports through the FastAPI backend.
- Presents classification metrics for standard and edge-case test sets.
- Displays intent, urgency, human-review, and all-fields accuracy.
- Shows individual test-case results when available.

### 6. Workflow Automation with n8n
- Integrates customer-support classification with an n8n workflow.
- Uses Ollama for local AI inference.
- Sends customer messages to the FastAPI classification endpoint.
- Routes cases according to whether human review is required.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Charts | Recharts |
| Backend | Python, FastAPI |
| Database | SQLite |
| Language model | Qwen 2.5 3B |
| Local model runtime | Ollama |
| Workflow automation | n8n |
| API testing | FastAPI Swagger UI |
| Automated tests | pytest |
| Version control | Git and GitHub |

## Architecture

```text
Customer
   |
   v
React + Vite Dashboard
   |
   v
FastAPI Backend
   |
   +----------------------+
   |                      |
   v                      v
Ollama                SQLite Database
Qwen2.5:3b            Orders and Review Cases
   |                      |
   +-----------+----------+
               |
               v
       Classification Results
               |
       +-------+--------+
       |                |
       v                v
Standard Support    Human Review Queue
                        |
                        v
                 Analytics Dashboard

Saved Evaluation Reports
               |
               v
       FastAPI /evaluation
               |
               v
        AI Evaluation Page

n8n Workflow
   |
   +----> Ollama
   |
   +----> FastAPI Classification API
```

## Prerequisites

Install the following before running the project:

- Python
- Node.js and npm
- Git
- Ollama
- Docker Desktop, if you want to run n8n using Docker

The commands below use Windows PowerShell.

## Getting Started

### 1. Clone the repository

```powershell
git clone https://github.com/vismaya-dinesh/ShopFlow-AI.git
cd ShopFlow-AI
```

### 2. Create and activate a Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use an appropriate execution-policy setting for your environment or activate the virtual environment through your IDE.

### 3. Install backend dependencies

If the repository contains `requirements.txt`, run:

```powershell
python -m pip install -r requirements.txt
```

If your project uses a different dependency installation method, follow the dependency files included in the repository.

### 4. Start Ollama

Install and start Ollama, then pull the model:

```powershell
ollama pull qwen2.5:3b
```

Confirm the model is available:

```powershell
ollama list
```

The application expects the local Ollama API at:

```text
http://localhost:11434
```

### 5. Start the FastAPI backend

From the project root, with the virtual environment activated:

```powershell
python -m uvicorn api.main:app --reload
```

Backend URLs:

- API: `http://localhost:8000`
- Swagger documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 6. Start the React frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local frontend URL shown in the terminal, normally:

```text
http://localhost:5173
```

For a production build, run these commands from the `frontend` directory:

```powershell
npm run lint
npm run build
```

## API Endpoints

The application exposes the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check backend health |
| GET | `/orders/{order_id}` | Retrieve an order |
| POST | `/classify` | Classify a customer message |
| GET | `/review-cases` | Retrieve human-review cases |
| GET | `/review-cases/{review_id}` | Retrieve a specific review case |
| POST | `/review-cases/{review_id}/complete` | Mark a review case as completed |
| GET | `/analytics` | Retrieve review analytics |
| GET | `/evaluation` | Retrieve saved evaluation reports |

Use `http://localhost:8000/docs` to inspect endpoint schemas and test requests.

## Evaluation Results

The saved benchmark reports for `qwen2.5:3b` currently show:

| Metric | Standard evaluation | Edge-case evaluation |
|---|---:|---:|
| Test cases | 30 | 10 |
| Intent accuracy | 100% | 100% |
| Urgency accuracy | 100% | 100% |
| Human-review accuracy | 100% | 100% |
| All-fields accuracy | 100% | 100% |

These figures describe the current saved test sets. They do not guarantee equivalent performance on unseen messages or production customer traffic.

## Running Tests

From the project root, activate the virtual environment and run:

```powershell
python -m pytest -v
```

The current development test run completed with **24 passing tests**.

## Running n8n

ShopFlow AI can connect to n8n for workflow automation.

If you are running n8n in Docker on Windows, a container can reach host services using `host.docker.internal`. For example:

```text
http://host.docker.internal:8000
http://host.docker.internal:11434
```

The configured workflow uses the classification API to create review cases and route customer requests according to the human-review decision.

The n8n interface is available at `http://localhost:5678` when the container is running.

**Note:** Import or configure the workflow separately if it is not included in the repository. Ensure the required services are running before executing it.

## Project Structure

```text
ShopFlow-AI/
├── api/
│   ├── database.py
│   ├── main.py
│   └── classifier.py
├── data/
│   └── shopflow.db
├── evals/
├── tests/
│   └── test_orders.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── package-lock.json
├── ai_evaluation_report.json
├── edge_case_evaluation_report.json
├── requirements.txt
└── README.md
```

This tree illustrates the main project components. Exact filenames and optional files may differ depending on the current repository version. Local databases, virtual environments, and generated evaluation reports may be excluded from version control.

## Design Principles

- **Local-first inference:** Uses a locally hosted language model rather than requiring a paid hosted LLM API.
- **Human oversight:** Flags selected customer cases for review instead of treating every AI prediction as a final decision.
- **Separation of concerns:** Keeps the frontend, backend, database, and workflow automation as distinct components.
- **Evaluation-driven development:** Uses saved benchmarks to measure classification performance.
- **API-based integration:** Connects the dashboard and automation workflow through backend endpoints.

## Future Improvements

- Add authentication and role-based access for reviewers.
- Introduce more diverse evaluation datasets and confidence-based escalation.
- Add structured logging and model-response monitoring.
- Add automated CI checks for tests and frontend builds.
- Improve production deployment configuration and environment-based API URLs.
- Export analytics and evaluation reports for further analysis.

## Disclaimer

This is a portfolio and development project. The included order records and benchmark results are for demonstration and testing. AI-generated classifications can be incorrect, and human judgment should be used when handling sensitive, disputed, or high-impact customer issues.

## Author

Developed as a portfolio project demonstrating AI-powered customer support, local LLM inference, API development, workflow automation, evaluation, and frontend dashboard engineering.

GitHub repository: https://github.com/vismaya-dinesh/ShopFlow-AI
