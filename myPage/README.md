# Hank Ku • Portfolio

Personal portfolio website showcasing machine learning projects, built with Vue 3 and a FastAPI backend.

## Tech Stack

**Frontend**
- Vue 3 + Vite
- Vue Router (History Mode)

**Backend**
- FastAPI (Python 3.11)
- PyTorch, gensim, CKIP-Transformers
- Ollama (RAG feature)

## Projects

| Project | Description |
|---------|-------------|
| Digit Recognition | CNN-based handwritten digit classifier |
| PTT Classifier | NLP model for PTT post board classification |
| Custom Neural Network | Interactive neural network visualizer |
| Vehicle Detection | YOLOv8-based vehicle detection |
| Classical NLP | Classical Chinese language model |
| Traffic Law RAG | Retrieval-Augmented Generation for traffic law Q&A |

## Local Development

```bash
docker compose -f docker-compose.dev.yml up --build
```

Frontend: http://localhost:5173  
Backend: http://localhost:8000

> ML model files are not included in the repo. Place them in `backend/models/` before starting.

## Production Deployment

```bash
docker compose up -d --build
```

Requires `.env` at project root and SSL certificates via certbot.
