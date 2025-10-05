# Gemini Safety Filter Solution

## Issue
Responses are still being filtered despite safety settings, showing:
> "Response was filtered by safety settings. Please try rephrasing your request."

## Root Cause
The safety settings format was incorrect. Gemini API requires using proper enums from `google.generativeai.types`.

## Solution Applied

### Updated `_gemini_chat()` function (lines 171-180)

**Changed from:**
```python
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    # ... etc
]
```

**Changed to:**
```python
from google.generativeai.types import HarmCategory, HarmBlockThreshold

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}
```

### Added Enhanced Logging

Added detailed logging to diagnose filtering issues:
- Logs finish reasons
- Logs safety ratings for each candidate
- Logs prompt feedback when blocked

## Alternative Solutions

### Option 1: Use a More Permissive Model
If `gemini-2.5-flash` continues to filter responses, switch to `gemini-1.5-pro`:

**Update `.env`:**
```env
GEMINI_MODEL_SUMMARY=gemini-1.5-pro
GEMINI_MODEL_REPLY=gemini-1.5-pro
```

### Option 2: Adjust Prompts to Be Less Triggering
Modify the system prompts to avoid words that might trigger filters:

**In `/suggest_reply` endpoint (around line 342):**
```python
system = (
    "You are a helpful customer support agent. "
    "Write a brief, professional response acknowledging the user's concern. "
    "Be empathetic and solution-focused."
)
```

**In `/summarize` endpoint (around line 289):**
```python
system = (
    "You are a product feedback analyst. "
    "Create a brief, neutral summary of the feedback in one sentence."
)
```

### Option 3: Use BLOCK_ONLY_HIGH Instead of BLOCK_NONE
If your API key doesn't support `BLOCK_NONE`, try:

```python
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}
```

## Testing

### 1. Restart the server
```powershell
cd d:\discrete\FEED\FEED\server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Watch the console logs
When you click "Suggest Reply" or "Generate Summary", check the server console for:
```
[GEMINI] Finish reasons: [...]
[GEMINI] Candidate 0 safety ratings: [...]
```

### 3. Test with different feedback
Try these test cases:
- ✅ Neutral: "The app is slow"
- ✅ Negative: "The feature doesn't work"
- ✅ Frustrated: "This is frustrating to use"

### 4. Check what's being blocked
If still blocked, the console will show which safety category triggered:
```
[GEMINI] Response blocked by safety filters despite BLOCK_NONE settings
[GEMINI] Candidate 0 safety ratings: [category: HARM_CATEGORY_..., probability: HIGH]
```

## If Still Blocked

### Fallback: Use OpenAI Instead
If Gemini continues to block responses, switch to OpenAI:

**Update `.env`:**
```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL_SUMMARY=gpt-4o-mini
OPENAI_MODEL_REPLY=gpt-4o-mini
```

The code already supports OpenAI as a fallback provider.

## Status

✅ **Safety settings updated to use proper enum format**  
✅ **Enhanced logging added for debugging**  
✅ **Multiple fallback options documented**  

---

**Next Steps:**
1. Restart server
2. Test with real feedback
3. Check console logs for blocking details
4. If still blocked, try Option 1, 2, or 3 above

**Date:** 2025-10-04
