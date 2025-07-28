from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import hmac
import hashlib
import base64

# Load environment variables from .env
load_dotenv()

# FastAPI app instance
app = FastAPI()

# CORS middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check or root route
@app.get("/")
async def root():
    return {"message": "AI Bookkeeping Agent is live!"}


# Analyze endpoint (stubbed for future Gemini AI integration)
@app.post("/analyze")
async def analyze_endpoint():
    # This is where you'll add file parsing + Gemini logic
    return {"status": "Analysis completed (stub)"}


# LemonSqueezy Webhook handler
@app.post("/webhook/lemonsqueezy")
async def lemonsqueezy_webhook(
    request: Request,
    x_signature: str = Header(None)
):
    secret = os.getenv("LEMON_WEBHOOK_SECRET")
    if not secret:
        return {"error": "Webhook secret missing from environment"}

    # Read raw body to verify signature
    raw_body = await request.body()

    # Compute expected signature
    expected_signature = base64.b64encode(
        hmac.new(secret.encode(), raw_body, hashlib.sha256).digest()
    ).decode()

    # Validate
    if not hmac.compare_digest(expected_signature, x_signature):
        return {"error": "Invalid webhook signature"}

    payload = await request.json()
    event = payload.get("meta", {}).get("event_name", "unknown")
    data = payload.get("data", {})

    print(f"? Webhook received: {event}")
    print(data)

    return {"status": "Webhook received", "event": event}