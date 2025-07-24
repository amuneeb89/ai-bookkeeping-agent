from fastapi import FastAPI, Request, HTTPException
import stripe
import os

app = FastAPI()

# Set your Stripe secret key (automatically pulled from env variables)
stripe.api_key = os.getenv("STRIPE_LIVE_SECRET_KEY")  # or STRIPE_SECRET_KEY if using one env var

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = os.getenv("STRIPE_LIVE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # ? Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("?? Payment succeeded:", session)

    # Handle more events if needed...

    return {"status": "success"}
