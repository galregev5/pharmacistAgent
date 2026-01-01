# Real-time AI Pharmacy Agent

## Phase 1: Project Scaffolding

### Tech Stack
- Backend: Python + Flask (Vanilla OpenAI API, no LangChain)
- Frontend: React (Vite)
- Database: SQLite (local file stored in `backend/data/`)

### Project Structure
- backend/
  - app/
  - data/
- frontend/

### Backend Setup
1. Create and activate a Python 3.10+ virtual environment.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Copy the environment template and set your key:
   ```bash
   cp backend/.env.example backend/.env
   # edit backend/.env and set OPENAI_API_KEY
   ```
4. (App entrypoint TBD in later phase.)

### Frontend Setup
1. Create the React app with Vite (from repository root):
   ```bash
   npm create vite@latest frontend -- --template react
   ```
2. Install required UI and API helpers (run inside `frontend/`):
   ```bash
   npm install axios lucide-react react-markdown
   ```
3. (Frontend entrypoint/config to be added in later phase.)

### Running (placeholder for next phase)
- Backend server: (instructions will be added once the Flask app file is created.)
- Frontend dev server: run `npm run dev` inside `frontend/` after the app is generated.
