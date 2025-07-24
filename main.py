from fastapi import FastAPI, Request, Header, HTTPException
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Load Stripe secret key and webhook secret
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


@app.get("/analyze/health")
async def health_check():
    return {"status": "ok"}


@app.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    try:
        payload = await request.body()

        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )

        # Log event
        print("?? Received event:", event["type"])

        # Handle the event
        if event["type"] == "payment_intent.succeeded":
            print("? Payment succeeded.")
        elif event["type"] == "invoice.paid":
            print("? Invoice paid.")
        else:
            print(f"Unhandled event type {event['type']}")

        return {"status": "success"}

    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        print("?? Webhook error:", e)
        raise HTTPException(status_code=400, detail="Webhook error")


@app.get("/")
async def root():
    return {"message": "Stripe Webhook API is running"}
