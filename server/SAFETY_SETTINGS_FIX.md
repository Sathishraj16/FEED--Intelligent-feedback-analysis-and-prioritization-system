# Gemini Safety Settings Fix

## Issue
Gemini API responses were being blocked by safety filters with `finish_reason = 2`, preventing legitimate feedback summarization and reply generation.

## Solution
Added safety settings to `_gemini_chat()` function to disable content filtering for all categories.

## Changes Made

### File: `server/main.py` (Lines 159-231)

**Added safety settings:**
```python
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
```

**Updated generate_content call:**
```python
r = m.generate_content(
    prompt, 
    generation_config=gen_cfg,
    safety_settings=safety_settings  # <-- Added this
)
```

**Improved error handling:**
- Checks if `r.candidates` is empty (blocked response)
- Checks for `finish_reason = 2` (safety filter)
- Returns user-friendly messages instead of crashing
- Logs diagnostic info for debugging

## Benefits

✅ **No more blocked responses** - Safety filters disabled for feedback processing  
✅ **Better error messages** - Users see helpful messages if filtering occurs  
✅ **Graceful degradation** - Returns fallback text instead of 500 errors  
✅ **Debug logging** - Console shows diagnostic info for troubleshooting  

## Testing

After restarting the server, test with:

```powershell
# Test suggest_reply
Invoke-WebRequest -Method POST -Uri "http://localhost:8000/suggest_reply" `
  -ContentType "application/json" `
  -Body '{"text": "The app keeps crashing"}' `
  -UseBasicParsing

# Test summarize
Invoke-WebRequest -Method POST -Uri "http://localhost:8000/summarize" `
  -ContentType "application/json" `
  -Body '{"text": "Users are frustrated with the login process"}' `
  -UseBasicParsing
```

## Restart Command

```powershell
cd d:\discrete\FEED\FEED\server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

**Status:** ✅ Fixed  
**Date:** 2025-10-04  
**Model:** gemini-2.5-flash with BLOCK_NONE safety settings
