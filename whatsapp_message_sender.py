# ============================================================
#  Le & Zel — WhatsApp Bulk Send
#  Reads guest list from a local CSV and sends a personalised
#  WhatsApp message to every guest with a phone number.
#
#  CSV FORMAT (with header row):
#    full_name, phone_number, guest_id
#
#  SETUP:
#    pip install twilio
#
#  RUN:
#    python 6_whatsapp_bulk_send.py
# ============================================================

import csv
import json
import time
from twilio.rest import Client

# ── Twilio credentials ────────────────────────────────────────
ACCOUNT_SID         = ""   # From Twilio Console → Account Info
AUTH_TOKEN          = ""                 # From Twilio Console → Account Info
FROM_NUMBER         = "+6589919363"                         # Your approved Twilio WhatsApp sender (no whatsapp: prefix)
# ─────────────────────────────────────────────────────────────

# ── CSV config ────────────────────────────────────────────────
CSV_FILE             = "guests.csv"                  # Path to your CSV file
# ─────────────────────────────────────────────────────────────

# ── Rate limiting ─────────────────────────────────────────────
DELAY_BETWEEN_SENDS  = 0.2
# ─────────────────────────────────────────────────────────────


def get_guests():
    """Read guest list from local CSV. Returns list of dicts."""
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def send_message_media(client, guest):
    """Send WhatsApp message type Media to a single guest. Returns (sid, status)."""
    TEMPLATE_SID        = "HX359f05d687494d2353a2bce6de42b232"
    phone       = str(guest["phone_number"]).strip()
    guest_id    = str(guest["guest_id"]).strip()

    if not phone.startswith("+"):
        phone = f"+65{phone}"

    message = client.messages.create(
        from_=f"whatsapp:{FROM_NUMBER}",
        to=f"whatsapp:{phone}",
        content_sid=TEMPLATE_SID,
        content_variables=json.dumps({
            "1": guest_id,
        }),
    )

    return message.sid, message.status

def send_reminder_message(client, guest, template_sid):
    """Send WhatsApp message to a single guest. Returns (sid, status)."""
    phone       = str(guest["phone_number"]).strip()
    if not phone.startswith("+"):
        phone = f"+65{phone}"

    message = client.messages.create(
        from_=f"whatsapp:{FROM_NUMBER}",
        to=f"whatsapp:{phone}",
        content_sid=template_sid,
    )
    return message.sid, message.status

def send_reminder_message_2_week(client, guest):
    return send_reminder_message(client, guest, "HXd4eec64ed2b805119b4fb8a9cf4d6582")

def send_reminder_message_1_week(client, guest):
    return send_reminder_message(client, guest, "HX85ce0adc53f8afcf3d351ae05f68b7f3")

def send_reminder_message_1_day(client, guest):
    return send_reminder_message(client, guest, "HXb79fb543dd50a24d6522a201bcbab763")

def send_reminder_message_0_day(client, guest):
    return send_reminder_message(client, guest, "HX3673955f7285c6cbf40999997b363fbf")

def send_message_after(client, guest):
    return send_reminder_message(client, guest, "HX7e1aaf2f76ac0bedb45fc757b9ddb7c4")


def bulk_send():
    print("📋 Reading guest list from CSV...")
    guests  = get_guests()
    to_send = [g for g in guests if str(g.get("phone_number", "")).strip()]
    skipped = len(guests) - len(to_send)

    print(f"   Total guests : {len(guests)}")
    print(f"   With number  : {len(to_send)}")
    print(f"   Skipped      : {skipped} (no phone number)")
    print()

    client     = Client(ACCOUNT_SID, AUTH_TOKEN)
    successful = []
    failed     = []

    for i, guest in enumerate(to_send, 1):
        name  = guest["full_name"].strip()
        phone = str(guest["phone_number"]).strip()
        gid   = str(guest["guest_id"]).strip()
        print(f"[{i}/{len(to_send)}] Sending to {name} ({phone}) — {gid}...", end=" ")

        try:
            sid, status = send_reminder_message_2_week(client, guest)
            #sid, status = send_reminder_message_1_week(client, guest)
            #sid, status = send_reminder_message_1_day(client, guest)
            #sid, status = send_reminder_message_0_day(client, guest)
            sid_media, status_media = send_message_media(client, guest)
            print(f"✅ {status} ({sid})")
            print(f"✅ {status_media} ({sid_media})")
            successful.append({"name": name, "phone": phone, "sid": sid})
            successful.append({"name": name, "phone": phone, "sid": sid_media})
        except Exception as e:
            print(f"❌ Failed: {e}")
            failed.append({"name": name, "phone": phone, "error": str(e)})

        time.sleep(DELAY_BETWEEN_SENDS)

    print()
    print("=" * 50)
    print(f"✅ Sent successfully : {len(successful)}")
    print(f"❌ Failed            : {len(failed)}")

    if failed:
        print()
        print("Failed guests:")
        for f in failed:
            print(f"  - {f['name']} ({f['phone']}): {f['error']}")


if __name__ == "__main__":
    bulk_send()
