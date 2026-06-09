# ============================================================
#  Le & Zel — WhatsApp FAQ Bot
#  Powered by Twilio + Flask
# ============================================================

import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# ── Twilio credentials ────────────────────────────────────────
# Set these in PythonAnywhere:
#   Dashboard → Web → your app → Environment variables section
ACCOUNT_SID  = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN   = os.environ.get("TWILIO_AUTH_TOKEN")
# ─────────────────────────────────────────────────────────────

# ── FAQ list ──────────────────────────────────────────────────
# Each entry is a tuple of (keywords, reply).
# Keywords are case-insensitive and matched as substrings,
# so "venue" will match "where is the venue?" too.
# Add as many keywords as needed per reply.
FAQS = [
    (
        ["venue", "location"],
        "The wedding venue is at Fullerton Bay Hotel, "
        "80 Collyer Quay, Singapore 049326. "
        "If you're coming by car, please remember to ask for parking validation. "
        "Raffles Place MRT is the nearest train station to the venue."
    ),
    (
        ["solemnisation", "nikah", "nikkah"],
        "If you are attending the solemnisation, please be seated by 9:30 am"             
    ),
    (
        ["dress", "code", "dresscode", "color", "scheme"],
        "Pastel-palette traditional Malay attire (or your own traditional attire). "
        "Please avoid shades of green and peach, as these are reserved for immediate family only."             
    ),
    (
        ["time", "program"],
        "Kindly arrive at The Clifford Pier by 10:50 am to register and enjoy the cocktail hour. "
        "The lunch reception will start promptly at 11:25 am"              
    ),
]

# ─────────────────────────────────────────────────────────────


@app.route("/webhook", methods=["POST"])
def webhook():
    incoming = request.form.get("Body", "").strip().lower()
    response = MessagingResponse()

    # Match against FAQ keywords
    reply = FALLBACK
    for keywords, answer in FAQS:
        if any(keyword in incoming for keyword in keywords):
            reply = answer
            break

    response.message(reply)
    return str(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
