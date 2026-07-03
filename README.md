# My Adventure

A full-stack choose-your-own-adventure game where players enter a theme, generate an interactive branching story, and continue the narrative through choices.

Live demo: https://myadventure.vercel.app/

## Highlights

- Theme-driven story generation with asynchronous job polling
- Branching narrative tree with playable story continuation
- Frontend and backend split for clean local development and production deployment
- Fallback story generation when the Hugging Face API token is unavailable
- SQLite for local development, PostgreSQL-ready for production

## Tech Stack

| Layer | Tech |
| --- | --- |
| Frontend | React, TypeScript, Vite |
| Backend | FastAPI, SQLAlchemy, Uvicorn |
| Deployment | Vercel frontend, Render backend |
| Story Generation | Hugging Face integration |

## Features

- Create a story by entering a custom theme
- Poll job status while the story is being generated
- Load and play through a complete branching story path
- Handle missing API credentials gracefully with a built-in fallback mode

## Project Structure

- `frontend/`: React UI, loading states, story generator, and story reader
- `backend/`: FastAPI app, routers, database layer, schemas, and story generation logic
- `api/`: Legacy Vercel entrypoint from earlier deployment experiments

## Local Development

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

By default, the frontend runs on `http://localhost:5173` and the backend runs on `http://localhost:8000`.

## Environment Variables

### Backend

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLite or PostgreSQL connection string |
| `ALLOWED_ORIGINS` | Comma-separated or JSON list of allowed frontend origins |
| `DEBUG` | `True` for local development, `False` for production |
| `HF_API_TOKEN` | Optional Hugging Face token |
| `HF_MODEL` | Optional model name, defaults to `moonshotai/Kimi-K2-Instruct-0905` |

## Deployment

- Frontend: https://myadventure.vercel.app/
- Backend: https://myadventure.onrender.com/

In production, the frontend points to the Render backend at `https://myadventure.onrender.com/`. In local development, it uses the Vite `/api` proxy.

## Implementation Notes

- FastAPI handles story creation, job polling, and complete story loading
- The backend uses a resilient configuration layer to avoid startup failures caused by missing environment values
- The app is designed to keep working even when the external model API is unavailable
