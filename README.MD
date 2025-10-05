# FEED - Intelligent Feedback Analysis System

## Overview
FEED helps businesses analyze and prioritize customer feedback at scale.  
It automatically ingests feedback (manual, CSV, APIs), analyzes sentiment, urgency, and impact, and generates actionable insights with AI summaries and response suggestions.

**Core Idea:** Focus on the right feedback.

---

## Tech Stack

**Backend:** Python, FastAPI, Supabase (PostgreSQL), NLTK, Google Gemini AI, Pandas, Uvicorn  
**Frontend:** Next.js 14, TypeScript, Tailwind CSS, React Hooks  
**AI & NLP:** Sentiment analysis (NLTK VADER), custom scoring, text normalization, AI summaries & responses  

---

## Architecture

Next.js Frontend → FastAPI Backend → Supabase DB
↓
AI Services (Gemini + NLP)

yaml
Copy code

**Data Flow:** Input → Normalization → NLP Analysis → Scoring → Database → Dashboard

---

## Key Features

- Dashboard & Analytics: Sentiment trends, priority table, impact vs urgency charts  
- CSV Import: Auto-column mapping, batch processing, deduplication  
- AI Features: Smart prioritization, auto-tagging, response suggestions, team assignment  

---

## Database Schema

| Column           | Type       | Description |
|-----------------|------------|-------------|
| id               | integer PK | Feedback ID |
| raw_text         | text       | Original feedback |
| source           | string     | Manual, CSV, API |
| created_at       | timestamp  | Submission time |
| normalized_text  | text       | Cleaned feedback |
| text_hash        | string     | Deduplication hash |
| sentiment        | float      | -1 to 1 |
| urgency          | float      | 0 to 1 |
| impact           | float      | 0 to 1 |
| priority         | float      | 0 to 1 |
| tags             | JSON array | Categories |
| metadata         | JSON       | Ratings, dates, etc. |

---

## Development

- Backend: FastAPI  
- Frontend: Next.js + TypeScript  
- DB: Supabase PostgreSQL  
- Env: `.env` configuration  
- CSV: Bulk upload with progress tracking

---

FEED is **scalable, intelligent, and actionable**, turning raw feedback into insights that matter.
