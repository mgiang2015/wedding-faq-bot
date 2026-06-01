# ============================================================
#  Le & Zel — WhatsApp FAQ Bot
#  Powered by Twilio + Flask
# ============================================================

import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# ── Twilio credentials ────────────────────────────────────────
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
        ["venue"],
        "The wedding venue is at Fullerton Bay Hotel, "
        "80 Collyer Quay, Singapore 049326. "
        "If you're coming by car, please remember to ask for parking validation. "
        "Raffles Place MRT is the nearest train station to the venue."
    ),
    (
        ["solemnisation", "nikah", "nikkah"],
        "Solemnisation details go here."              # ← replace with your actual reply
    ),
]

# ── Fallback reply (no FAQ matched) ──────────────────────────
FALLBACK = (
    "Sorry, we didn't quite catch that! "
    "For further assistance, please approach our registration table "
    "or contact the wedding coordinators directly."
)
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
    app.run(debug=True)
