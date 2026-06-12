# ============================================================
#  Le & Zel — WhatsApp FAQ Bot with Claude AI
#  Powered by Twilio + Flask + Anthropic Claude Haiku
#
#  SETUP (Render):
#  1. Push this file, requirements.txt, and render.yaml to GitHub
#  2. Connect repo to Render → Web Service
#  3. Set environment variables in Render dashboard:
#       ANTHROPIC_API_KEY  → from console.anthropic.com
#       TWILIO_ACCOUNT_SID → from Twilio Console
#       TWILIO_AUTH_TOKEN  → from Twilio Console
#  4. Deploy — webhook URL: https://<your-app>.onrender.com/webhook
#  5. Set that URL in Twilio Console → Messaging → Senders →
#     WhatsApp → "A message comes in" → HTTP POST
# ============================================================

import os
import anthropic
from twilio.rest import Client as TwilioClient
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# ── Credentials (set as environment variables on Render) ──────
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = "+6589919363"
# ─────────────────────────────────────────────────────────────

# ── Nikah interest notifications ─────────────────────────────
NIKAH_NOTIFY_NUMBERS = ["+6583504556"]
# ─────────────────────────────────────────────────────────────

# ── System prompt — all wedding knowledge lives here ──────────
SYSTEM_PROMPT = """
You are a warm and friendly wedding assistant for the wedding of Illyssa Zelda & Ikhlas Le.
Your name is Link. You help guests with questions about the wedding.
Keep your replies concise, friendly, and conversational — this is WhatsApp, not an essay.
If a question is unrelated to the wedding, politely let them know you can only help with wedding-related questions.
If you are unsure about something not covered below, ask them to approach the registration table or contact the couple directly.

IMPORTANT: If the guest expresses interest in attending the solemnisation / nikah / nikkah, you must:
1. Reply warmly saying their interest has been noted and we'll see them at 9:30am at Clifford Pier.
2. Start your reply with the tag [NIKAH_INTEREST] on its own line — this is used by the system to notify the couple. Remove this tag from what you show the guest.

Here is everything you know about the wedding:

--- GENERAL ---
Wedding of: Illyssa Zelda & Ikhlas Le
Date: 20 June 2026
Website: https://www.lezel.rsvp

--- SCHEDULE ---
- Solemnisation (intimate, close family & friends only): guests to be seated by 9:30 AM.
- Cocktail hour: guests to arrive at The Clifford Pier by 10:50 AM to register and enjoy the cocktail hour.
- Lunch reception: starts promptly at 11:25 AM.
- General recommendation: arrive from 10:50 AM onwards if not attending the solemnisation.

--- VENUE ---
The Clifford Pier, Fullerton Bay Hotel
80 Collyer Quay, Singapore 049326
Nearest MRT: Raffles Place MRT
Parking: available at the venue. Complimentary parking coupons available — guests should have informed the couple in advance if driving.
Parking validation: ask for it at the venue.

--- DRESS CODE ---
Traditional Malay attire (or your own traditional attire if preferred).
Pastel palette — use the colour palette on the website as inspiration, no need to match exactly.
Please AVOID: shades of green and peach (reserved for immediate family only), dark colours, and casual attire.

--- SEATING ---
Yes, there is assigned seating for the reception. Ushers will assist guests on the day.
Guests can also scan their QR code (on their invitation) to find their table number after checking in.
If you'd like to know who you're sitting with, please let the couple know

--- RSVP ---
RSVP deadline was Sunday, 19 April 2026.

--- PLUS ONES ---
Invitations are extended only to those named on the invitation. No plus ones, due to venue capacity.

--- CHILDREN ---
As much as we love your little ones, we have chosen to keep our celebration an adults-only event. We hope this allows everyone to relax and enjoy the day with us.

--- PRAYER ROOM ---
Yes, a prayer room will be available at the venue.

--- PHOTOGRAPHY ---
Guests are welcome to take photos. Please avoid blocking the photographers and videographers who will be moving around during the event.

--- CHECK-IN ---
Guests should scan the QR code on their invitation at the registration table to check in.
After checking in, they can scan again to see their table number on their phone.

--- RESPONSE TO PLEASANTRIES ---
If guest responds with pleasantries such as thank you / ty / thanks / terimah kasih, politely say you're welcome and if you have any other questions, feel free to ask
""".strip()
# ─────────────────────────────────────────────────────────────


def notify_nikah_interest(guest_number, guest_message):
    """Send a WhatsApp notification to the couple when a guest expresses nikah interest."""
    try:
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        notification = (
            f"💍 *Nikah interest alert!*\n"
            f"A guest ({guest_number}) has expressed interest in attending the solemnisation.\n"
            f"Their message: \"{guest_message}\""
        )
        for number in NIKAH_NOTIFY_NUMBERS:
            twilio_client.messages.create(
                from_=f"whatsapp:{TWILIO_FROM_NUMBER}",
                to=f"whatsapp:{number}",
                body=notification,
            )
    except Exception as e:
        pass  # Don't let notification failure affect the guest's reply


@app.route("/webhook", methods=["POST"])
def webhook():
    incoming = request.form.get("Body", "").strip()
    sender   = request.form.get("From", "unknown")
    response = MessagingResponse()

    if not incoming:
        response.message("Hi there! I'm Link, the wedding assistant for Le & Zel's big day 💍 How can I help you?")
        return str(response)

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        result = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": incoming}
            ],
        )
        reply = result.content[0].text.strip()

        # Check if Claude flagged nikah interest
        if reply.startswith("[NIKAH_INTEREST]"):
            reply = reply.replace("[NIKAH_INTEREST]", "").strip()
            notify_nikah_interest(sender, incoming)

    except Exception as e:
        reply = (
            "Sorry, I'm having a little trouble right now! "
            "Please approach our registration table or visit https://www.lezel.rsvp for more info."
        )

    response.message(reply)
    return str(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
