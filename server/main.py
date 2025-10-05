import os
from pathlib import Path
from typing import Any, Dict
import tempfile
import shutil

from fastapi import FastAPI, HTTPException, Path as FPath, Query, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
from math import isnan

# NLP utils (make sure server/nlp.py exists as provided earlier)
from nlp import (
    normalize_text,
    sha256_hex,
    sentiment_compound,
    score_urgency,
    score_impact,
    score_priority,
    simple_tags,
)



# --- Gemini (optional) ---
try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None  # type: ignore

# --- Load .env from this folder (server/.env) ---
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

def _mask(s: str | None) -> str:
    if not s:
        return "MISSING"
    return s[:8] + "…" + s[-4:]

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_SUMMARY = os.getenv("OPENAI_MODEL_SUMMARY", "gpt-4o-mini")
OPENAI_MODEL_REPLY = os.getenv("OPENAI_MODEL_REPLY", "gpt-4o-mini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_SUMMARY = os.getenv("GEMINI_MODEL_SUMMARY", "gemini-2.5-flash")
GEMINI_MODEL_REPLY = os.getenv("GEMINI_MODEL_REPLY", "gemini-2.5-flash")

# Helpful masked prints at startup
print("[ENV] .env exists:", ENV_PATH.exists())
print("[ENV] SUPABASE_URL:", _mask(SUPABASE_URL))
print("[ENV] SUPABASE_SERVICE_ROLE:", _mask(SUPABASE_SERVICE_ROLE))
print("[ENV] OPENAI_API_KEY set:", "YES" if OPENAI_API_KEY else "NO")
print("[ENV] GEMINI_API_KEY set:", "YES" if GEMINI_API_KEY else "NO")
if not GEMINI_API_KEY:
    # Extra hint to debug dotenv loading in dev
    try:
        import io
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            head = f.read(256)
        print("[ENV DEBUG] First 256 bytes of .env loaded (truncated):", head.replace("\n", "\\n"))
    except Exception:
        pass

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE in environment.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)

_oai_client = None
if OPENAI_API_KEY and OpenAI is not None:
    try:
        _oai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as _e:  # pragma: no cover
        print("[WARN] Failed to init OpenAI client:", _e)

_gemini_ready = False
if GEMINI_API_KEY and genai is not None:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_ready = True
    except Exception as _e:  # pragma: no cover
        print("[WARN] Failed to init Gemini:", _e)


app = FastAPI(title="FEED API", version="0.5.0")

# Allow your Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Schemas ----------
class EchoIn(BaseModel):
    text: str

class IngestIn(BaseModel):
    text: str
    source: str | None = "manual"

class SummarizeIn(BaseModel):
    id: int | None = None
    text: str | None = None

class SuggestReplyIn(BaseModel):
    id: int | None = None
    text: str | None = None
    sentiment: float | None = None
    urgency: float | None = None

# ---------- Helpers ----------
def _compute_signals_for_text(text: str) -> Dict[str, Any]:
    """Compute all signals for a given raw text."""
    tnorm = normalize_text(text)
    thash = sha256_hex(tnorm)
    compound = sentiment_compound(text)     # use original text for sentiment
    urgency = score_urgency(tnorm, compound)
    impact = score_impact(tnorm)
    priority = score_priority(urgency, impact)
    tags = simple_tags(tnorm, compound)
    return {
        "text_norm": tnorm,
        "text_hash": thash,
        "sentiment": compound,
        "urgency": urgency,
        "impact": impact,
        "priority": priority,
        "tags": tags,
    }

def _ensure_text_from_id(fid: int) -> Dict[str, Any]:
    got = supabase.table("feedback").select("id, raw_text, sentiment, urgency, impact, priority, tags").eq("id", fid).single().execute()
    data = got.data
    if not data:
        raise HTTPException(status_code=404, detail=f"Row id={fid} not found")
    return data

def _generate_action_analysis(feedback: str, sentiment: float, urgency: float, priority: float, impact: float, tags: list) -> Dict[str, str]:
    """Generate Next Step and Responsible Team based on feedback analysis."""
    
    # Predefined teams
    TEAMS = [
        "Engineering (Core App Team)",
        "Engineering (Frontend Team)", 
        "Engineering (Performance Team)",
        "Product Management",
        "Customer Success/Support",
        "Finance/Billing Team",
        "UX Design"
    ]
    
    # Convert tags to lowercase for easier matching
    tags_lower = [tag.lower() if isinstance(tag, str) else str(tag).lower() for tag in (tags or [])]
    feedback_lower = feedback.lower()
    
    # Determine responsible team based on content analysis
    responsible_team = _determine_responsible_team(feedback_lower, tags_lower, TEAMS)
    
    # Generate next step based on priority, urgency, and content
    next_step = _determine_next_step(feedback_lower, tags_lower, priority, urgency, sentiment, impact)
    
    # Try AI enhancement if available, with fallback to rule-based
    try:
        ai_analysis = _enhance_with_ai(feedback, sentiment, urgency, priority, impact, tags, responsible_team, next_step)
        return ai_analysis
    except Exception as e:
        print(f"[ACTION_ANALYSIS] AI enhancement failed, using rule-based: {e}")
        return {
            "next_step": next_step[:80],  # Ensure max 80 chars
            "responsible_team": responsible_team
        }

def _determine_responsible_team(feedback_lower: str, tags_lower: list, teams: list) -> str:
    """Determine responsible team based on content and tags."""
    
    # Finance/Billing keywords
    if any(word in feedback_lower for word in ['payment', 'billing', 'invoice', 'subscription', 'charge', 'refund', 'price', 'cost']):
        return "Finance/Billing Team"
    
    # UX Design keywords
    if any(word in feedback_lower for word in ['design', 'color', 'layout', 'visual', 'ugly', 'beautiful', 'interface']):
        return "UX Design"
    
    # Performance keywords
    if any(word in feedback_lower for word in ['slow', 'fast', 'performance', 'loading', 'lag', 'timeout', 'speed']):
        return "Engineering (Performance Team)"
    
    # Frontend keywords
    if any(word in feedback_lower for word in ['button', 'click', 'ui', 'display', 'screen', 'page', 'form', 'input']):
        return "Engineering (Frontend Team)"
    
    # Feature request keywords
    if any(word in feedback_lower for word in ['feature', 'add', 'wish', 'would like', 'suggestion', 'improve']):
        return "Product Management"
    
    # Support/how-to keywords
    if any(word in feedback_lower for word in ['how to', 'help', 'tutorial', 'guide', 'setup', 'account']):
        return "Customer Success/Support"
    
    # Check tags
    if 'bug' in tags_lower or 'crash' in tags_lower or 'error' in tags_lower:
        return "Engineering (Core App Team)"
    if 'feature_request' in tags_lower:
        return "Product Management"
    if 'billing' in tags_lower:
        return "Finance/Billing Team"
    
    # Default to Core App Team for technical issues
    return "Engineering (Core App Team)"

def _determine_next_step(feedback_lower: str, tags_lower: list, priority: float, urgency: float, sentiment: float, impact: float) -> str:
    """Generate next step based on analysis."""
    
    # High priority/urgent bugs
    if (priority >= 0.7 or urgency >= 0.7) and ('bug' in tags_lower or 'crash' in feedback_lower or 'error' in feedback_lower):
        return "Create P1/Critical ticket and reproduce bug in staging environment"
    
    # Medium priority bugs
    if 'bug' in tags_lower or 'error' in feedback_lower or 'broken' in feedback_lower:
        return "Review logs for related errors and add to sprint backlog"
    
    # Performance issues
    if any(word in feedback_lower for word in ['slow', 'performance', 'loading', 'lag', 'timeout']):
        return "Review database queries and investigate caching issues"
    
    # Feature requests
    if any(word in feedback_lower for word in ['feature', 'add', 'wish', 'suggestion']) or 'feature_request' in tags_lower:
        return "Add to Product Backlog and schedule user interview"
    
    # UX/Design issues
    if any(word in feedback_lower for word in ['confusing', 'hard to find', 'difficult', 'unclear']):
        return "Draft new help documentation and schedule design review"
    
    # Billing issues
    if any(word in feedback_lower for word in ['payment', 'billing', 'invoice', 'charge']):
        return "Review account billing status and contact customer"
    
    # High impact issues
    if impact >= 0.7:
        return "Escalate to team lead and create detailed investigation plan"
    
    # Default action
    return "Review feedback details and assign to appropriate team member"

def _enhance_with_ai(feedback: str, sentiment: float, urgency: float, priority: float, impact: float, tags: list, team: str, step: str) -> Dict[str, str]:
    """Use AI to enhance the rule-based analysis."""
    
    system = """You are an AI Action Analyzer for customer feedback. Generate two outputs:

1. NEXT_STEP: A single, clear action item (max 80 chars, verb-based command)
2. RESPONSIBLE_TEAM: Select from these teams only:
   - Engineering (Core App Team)
   - Engineering (Frontend Team)
   - Engineering (Performance Team)
   - Product Management
   - Customer Success/Support
   - Finance/Billing Team
   - UX Design

Respond in this exact format:
NEXT_STEP: [action]
RESPONSIBLE_TEAM: [team]"""

    user = f"""Feedback: {feedback}
Priority: {priority:.2f} | Urgency: {urgency:.2f} | Impact: {impact:.2f} | Sentiment: {sentiment:.2f}
Tags: {tags}

Current analysis:
- Team: {team}
- Step: {step}

Provide optimized analysis:"""

    try:
        response = _gemini_chat(GEMINI_MODEL_REPLY, system, user)
        
        # Parse AI response
        lines = response.strip().split('\n')
        next_step = step  # fallback
        responsible_team = team  # fallback
        
        for line in lines:
            if line.startswith('NEXT_STEP:'):
                next_step = line.replace('NEXT_STEP:', '').strip()[:80]
            elif line.startswith('RESPONSIBLE_TEAM:'):
                responsible_team = line.replace('RESPONSIBLE_TEAM:', '').strip()
        
        return {
            "next_step": next_step,
            "responsible_team": responsible_team
        }
    except Exception:
        # Return rule-based analysis if AI fails
        return {
            "next_step": step[:80],
            "responsible_team": team
        }

def _oai_chat(model: str, system: str, user: str) -> str:
    if not _oai_client:
        raise HTTPException(status_code=503, detail="OpenAI not configured")
    resp = _oai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
        max_tokens=120,
    )
    return (resp.choices[0].message.content or "").strip()

def _gemini_chat(model: str, system: str, user: str) -> str:
    if not _gemini_ready:
        raise HTTPException(status_code=503, detail="Gemini not configured")
    # Gemini doesn't use system/user the same way; combine into one prompt
    prompt = f"{system}\n\n{user}"
    try:
        # Generation config for consistent outputs
        gen_cfg = {
            "temperature": 0.2,
            "max_output_tokens": 160,
        }
       
        # Safety settings to prevent blocking legitimate feedback responses
        # Use BLOCK_ONLY_HIGH to allow most content while blocking extreme cases
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
       
        m = genai.GenerativeModel(model)
        r = m.generate_content(
            prompt,
            generation_config=gen_cfg,
            safety_settings=safety_settings
        )
        
        # Check if response was blocked
        if not r.candidates:
            print("[GEMINI] Response blocked - no candidates returned")
            print(f"[GEMINI] Prompt feedback: {getattr(r, 'prompt_feedback', None)}")
            return "Unable to generate response due to content policy. Please try rephrasing."
        
        # Try to access r.text safely - it can throw ValueError even if hasattr returns True
        try:
            if hasattr(r, "text") and r.text and r.text.strip():
                return r.text.strip()
        except ValueError as ve:
            # r.text threw an error (usually finish_reason = 2 for safety)
            print(f"[GEMINI] ValueError accessing r.text: {ve}")
            # Fall through to try alternate methods below
        
        # Fallback: join all parts' text if present
        txt_parts = []
        if getattr(r, "candidates", None):
            try:
                for cand in r.candidates:
                    if getattr(cand, "content", None) and getattr(cand.content, "parts", None):
                        for p in cand.content.parts:
                            t = getattr(p, "text", None)
                            if t:
                                txt_parts.append(t)
            except Exception:
                pass
        
        txt = " ".join(txt_parts).strip()
        if txt:
            return txt
        
        # If still empty, check finish reason
        diag = {
            "prompt_feedback": getattr(r, "prompt_feedback", None),
            "finish_reasons": [getattr(c, "finish_reason", None) for c in getattr(r, "candidates", [])],
        }
        print("[GEMINI DIAG] Empty text from response:", diag)
       
        # Check if blocked by safety filters (finish_reason = 2 or SAFETY)
        finish_reasons = [getattr(c, "finish_reason", None) for c in getattr(r, "candidates", [])]
        print(f"[GEMINI] Finish reasons: {finish_reasons}")
        
        # Also check safety ratings
        if r.candidates:
            for idx, cand in enumerate(r.candidates):
                safety_ratings = getattr(cand, "safety_ratings", None)
                if safety_ratings:
                    print(f"[GEMINI] Candidate {idx} safety ratings: {safety_ratings}")
        
        if 2 in finish_reasons or "SAFETY" in str(finish_reasons):
            print("[GEMINI] Response blocked by safety filters despite BLOCK_NONE settings")
            print(f"[GEMINI] Original prompt length: {len(prompt)} chars")
            # Return a generic but helpful response instead of error message
            if "reply" in prompt.lower() or "respond" in prompt.lower():
                return "Thank you for your feedback. We're looking into this issue and will get back to you shortly."
            else:
                return "Unable to process this content. Please try with different wording."
       
        return "Unable to generate response. Please try again."
        
    except Exception as e:
        # Log full exception for debugging while keeping HTTP error concise
        try:
            import traceback
            traceback.print_exc()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")

def _chat(provider: str | None, model: str, system: str, user: str) -> str:
    """Provider-agnostic chat. provider: 'openai' | 'gemini' | None (auto)."""
    prov = (provider or "").lower().strip() or os.getenv("AI_PROVIDER", "").lower().strip()
    if prov == "openai":
        return _oai_chat(model, system, user)
    if prov == "gemini":
        return _gemini_chat(model, system, user)
    # auto: prefer OpenAI if configured, else Gemini
    if _oai_client:
        return _oai_chat(model, system, user)
    if _gemini_ready:
        return _gemini_chat(model, system, user)
    raise HTTPException(status_code=503, detail="No AI provider configured")

# ---------- Routes ----------
@app.get("/")
def root():
    return {"ok": True, "service": "FEED API (Supabase)"}

@app.post("/echo")
def echo(payload: EchoIn):
    return {"you_sent": payload.text, "length": len(payload.text)}

@app.post("/ingest")
def ingest(payload: IngestIn):
    """
    Ingest a piece of feedback:
      - normalize + hash (exact dedup helper)
      - compute sentiment/urgency/impact/priority + tags
      - insert into Supabase
    """
    try:
        signals = _compute_signals_for_text(payload.text)
        row: Dict[str, Any] = {
            "raw_text": payload.text,
            "source": payload.source,
            **signals,
        }
        resp = supabase.table("feedback").insert(row).execute()
        data = resp.data or []
        if not data:
            raise RuntimeError("Insert returned no data")
        return {"saved": True, "id": data[0].get("id"), "priority": signals["priority"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase insert error: {e}")

@app.post("/summarize")
async def summarize(request: Request):
    """Generate a one-line summary from provided text or feedback ID.

    Accepts JSON body with either:
    - 'text' or 'feedback' field (direct text)
    - 'id' field (fetch from database)
    """
    try:
        try:
            data = await request.json()
        except Exception as e:
            # Handle malformed JSON or empty body
            error_msg = f"Invalid JSON in request body: {str(e)}"
            print(f"[ERROR] summarize JSON parsing failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        if not data:
            raise HTTPException(status_code=400, detail="Empty request body. Please provide 'id', 'text', or 'feedback' field")

        # Option 1: Accept 'id' and fetch from database
        fid = data.get("id")
        if fid:
            row = _ensure_text_from_id(fid)
            text = row.get("raw_text")
        else:
            # Option 2: Accept both 'text' and 'feedback' fields
            text = data.get("text") or data.get("feedback")
        
        if not text:
            available_fields = list(data.keys()) if data else []
            error_msg = f"Missing 'id', 'text', or 'feedback' in request. Available fields: {available_fields}"
            raise HTTPException(status_code=400, detail=error_msg)

        system = "You are an expert product support AI. Summarize feedback into one concise, actionable line."
        user = f"Text: {text}\nOutput only the summary, no quotes."
        summary = _gemini_chat(GEMINI_MODEL_SUMMARY, system, user)
        return {"summary": summary}
    except HTTPException:
        raise
    except Exception as e:
        try:
            print("Error in summarize:", e)
            import traceback; traceback.print_exc()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_action")
async def analyze_action(request: Request):
    """Generate AI Action Analysis for feedback - provides Next Step and Responsible Team.

    Accepts JSON body with either:
    - 'feedback' or 'text' field (direct text)
    - 'id' field (fetch from database with all signals)
    Optional: 'sentiment', 'urgency', 'priority', 'impact', 'tags' fields
    
    Returns: {"next_step": "Action item", "responsible_team": "Team name"}
    """
    try:
        try:
            data = await request.json()
        except Exception as e:
            error_msg = f"Invalid JSON in request body: {str(e)}"
            print(f"[ERROR] analyze_action JSON parsing failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        if not data:
            raise HTTPException(status_code=400, detail="Empty request body. Please provide 'id', 'feedback', or 'text' field")

        # Option 1: Accept 'id' and fetch from database
        fid = data.get("id")
        if fid:
            row = _ensure_text_from_id(fid)
            feedback = row.get("raw_text")
            sentiment = data.get("sentiment") or row.get("sentiment") or 0
            urgency = data.get("urgency") or row.get("urgency") or 0
            priority = data.get("priority") or row.get("priority") or 0
            impact = data.get("impact") or row.get("impact") or 0
            tags = data.get("tags") or row.get("tags") or []
        else:
            # Option 2: Accept direct fields
            feedback = data.get("feedback") or data.get("text")
            sentiment = data.get("sentiment") or 0
            urgency = data.get("urgency") or 0
            priority = data.get("priority") or 0
            impact = data.get("impact") or 0
            tags = data.get("tags") or []
        
        if not feedback:
            available_fields = list(data.keys()) if data else []
            error_msg = f"Missing 'id', 'feedback', or 'text' in request. Available fields: {available_fields}"
            raise HTTPException(status_code=400, detail=error_msg)

        # Generate action analysis
        analysis = _generate_action_analysis(feedback, sentiment, urgency, priority, impact, tags)
        
        return {
            "next_step": analysis["next_step"],
            "responsible_team": analysis["responsible_team"]
        }
    except HTTPException:
        raise
    except Exception as e:
        try:
            print("Error in analyze_action:", e)
            import traceback; traceback.print_exc()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/suggest_reply")
async def suggest_reply(request: Request):
    """Legacy endpoint - now returns action analysis in reply format for backward compatibility.
    
    This maintains compatibility with existing frontend while providing action-oriented responses.
    """
    try:
        # Use the new action analyzer
        analysis_response = await analyze_action(request)
        
        # Format as a "reply" for backward compatibility
        next_step = analysis_response["next_step"]
        responsible_team = analysis_response["responsible_team"]
        
        # Create a reply-style response that includes the action analysis
        reply = f"Action Required: {next_step}\n\nAssigned to: {responsible_team}"
        
        return {"reply": reply}
    except Exception as e:
        try:
            print("Error in suggest_reply (legacy):", e)
            import traceback; traceback.print_exc()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpis")
def kpis(days: int = Query(30, ge=1, le=180)):
    """Basic KPIs and sentiment-over-time for the last N days."""
    try:
        since = datetime.utcnow() - timedelta(days=days)
        # Pull a reasonable window; if dataset is large, consider pagination or DB-side aggregation
        resp = (
            supabase.table("feedback")
            .select("id, created_at, priority, urgency, impact, sentiment")
            .order("id", desc=True)
            .limit(2000)
            .execute()
        )
        rows = resp.data or []

        # Filter by date if available
        def _parse_dt(s: str | None):
            if not s:
                return None
            try:
                return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                return None

        rows = [r for r in rows if (dt := _parse_dt(r.get("created_at"))) and dt >= since]

        total = len(rows)
        urgent = sum(1 for r in rows if (r.get("urgency") or 0) >= 0.66)
        pos = sum(1 for r in rows if (r.get("sentiment") or 0) >= 0.2)
        neg = sum(1 for r in rows if (r.get("sentiment") or 0) <= -0.2)
        avg_priority = (
            (sum((r.get("priority") or 0) for r in rows) / total) if total else 0.0
        )

        # sentiment by day
        by_day: Dict[str, Dict[str, float]] = {}
        for r in rows:
            dt = _parse_dt(r.get("created_at"))
            if not dt:
                continue
            day = dt.strftime("%Y-%m-%d")
            d = by_day.setdefault(day, {"sum": 0.0, "n": 0})
            d["sum"] += float(r.get("sentiment") or 0)
            d["n"] += 1
        series = [
            {"date": day, "avg_sentiment": (v["sum"] / v["n"]) if v["n"] else 0.0}
            for day, v in sorted(by_day.items())
        ]

        return {
            "total": total,
            "urgent": urgent,
            "positive": pos,
            "negative": neg,
            "avg_priority": avg_priority,
            "sentiment_over_time": series,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KPIs error: {e}")

@app.get("/feedback")
def list_feedback(limit: int = 10):
    """Recent feedback by id desc."""
    try:
        resp = (
            supabase.table("feedback")
            .select("*")
            .order("id", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase select error: {e}")

@app.get("/prioritized")
def prioritized(limit: int = 10):
    try:
        resp = (
            supabase.table("feedback")
            .select("*")
            .order("priority", desc=True)   # client is PostgREST; nulls usually sort first in DESC
            .execute()
        )
        data = resp.data or []
        # filter out nulls and take top N
        data = [d for d in data if d.get("priority") is not None]
        # already roughly sorted; ensure order client-side
        data.sort(key=lambda d: d.get("priority") or 0, reverse=True)
        return data[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase select error: {e}")


@app.post("/rescore/{id}")
def rescore_one(id: int = FPath(..., ge=1)):
    """
    Recompute signals for a single row id and update it.
    Useful to backfill rows created before scoring was added.
    """
    try:
        got = supabase.table("feedback").select("id, raw_text").eq("id", id).single().execute()
        row = got.data
        if not row:
            raise HTTPException(status_code=404, detail=f"Row id={id} not found")

        signals = _compute_signals_for_text(row["raw_text"])
        supabase.table("feedback").update(signals).eq("id", id).execute()
        return {"rescored": True, "id": id, **signals}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rescore error: {e}")

@app.post("/rescore_all")
def rescore_all(limit: int = Query(50, ge=1, le=500)):
    """
    Re-score the latest N rows (default 50).
    Handy to backfill older rows that have null analytics fields.
    """
    try:
        got = (
            supabase.table("feedback")
            .select("id, raw_text")
            .order("id", desc=True)
            .limit(limit)
            .execute()
        )
        rows = got.data or []
        updated = []
        for r in rows:
            signals = _compute_signals_for_text(r["raw_text"])
            supabase.table("feedback").update(signals).eq("id", r["id"]).execute()
            updated.append({"id": r["id"], **signals})
        return {"rescored": len(updated), "items": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rescore-all error: {e}")


@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload and import App Store reviews from a CSV file.
    
    Expected CSV columns (auto-detected):
    - Review text: 'review', 'content', 'text', 'comment', 'feedback', 'body', 'message'
    - Rating: 'rating', 'score', 'stars', 'star'
    - Title: 'title', 'subject', 'headline', 'summary'
    - Date: 'date', 'created', 'submitted', 'time', 'timestamp'
    - App Version: 'version', 'app_version', 'build'
    - Reviewer: 'reviewer', 'user', 'author', 'name'
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    try:
        # Import the CSV importer here to avoid circular imports
        from csv_importer import AppStoreReviewImporter
        
        # Create a temporary file to save the uploaded CSV
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            # Copy the uploaded file content to the temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Import the CSV
            importer = AppStoreReviewImporter()
            stats = importer.import_csv(temp_file_path, batch_size=50)
            
            return {
                "success": True,
                "message": f"Successfully imported {stats['imported']} reviews",
                "stats": stats,
                "filename": file.filename
            }
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing CSV: {str(e)}")


@app.get("/import-status")
def get_import_status():
    """Get statistics about imported data."""
    try:
        # Get total count
        total_resp = supabase.table("feedback").select("id", count="exact").execute()
        total_count = total_resp.count or 0
        
        # Get count by source
        app_store_resp = supabase.table("feedback").select("id", count="exact").eq("source", "app_store_csv").execute()
        app_store_count = app_store_resp.count or 0
        
        # Get recent imports (last 24 hours)
        since = datetime.utcnow() - timedelta(hours=24)
        recent_resp = (
            supabase.table("feedback")
            .select("id", count="exact")
            .eq("source", "app_store_csv")
            .gte("created_at", since.isoformat())
            .execute()
        )
        recent_count = recent_resp.count or 0
        
        return {
            "total_feedback": total_count,
            "app_store_reviews": app_store_count,
            "recent_imports_24h": recent_count,
            "other_sources": total_count - app_store_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
