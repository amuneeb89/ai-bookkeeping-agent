from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust if needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example root endpoint
@app.get("/")
async def root():
    return {"message": "AI Bookkeeping Agent is live."}


# ?? Analyze Route (placeholder logic)
@app.post("/analyze")
async def analyze_bookkeeping():
    # TODO: Add file processing + Gemini logic
    return {"status": "Analysis complete."}


# ?? LemonSqueezy Webhook Listener
from fastapi import Request, Header
import hmac
import hashlib
import base64

@app.post("/webhook/lemonsqueezy")
async def lemonsqueezy_webhook(request: Request, x_signature: str = Header(None)):
    secret = os.getenv("LEMON_WEBHOOK_SECRET")
    raw_body = await request.body()

    expected_signature = base64.b64encode(
        hmac.new(
            secret.encode(),
            msg=raw_body,
            digestmod=hashlib.sha256
        ).digest()
    ).decode()

    if not hmac.compare_digest(expected_signature, x_signature):
        return {"error": "Invalid signature"}

    payload = await request.json()
    event_type = payload.get("meta", {}).get("event_name", "unknown")
    data = payload.get("data", {})

    # Log or handle events
    print(f"? Webhook received: {event_type}")
    print(data)

    return {"status": "Webhook processed"}
