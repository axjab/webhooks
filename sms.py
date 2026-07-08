#!/usr/bin/env python3

import sys, requests, time
from pykit import Configurator, Webhook, Notifier, Notification, env


def normalize_sms(webhook:Webhook):
    if "application/json" in webhook.content_type:
        return webhook.payload

    if "application/x-www-form-urlencoded" in webhook.content_type:
        payload = webhook.payload
        _from = payload["from"].strip()
        _to   = payload["to"].strip()
        if not _from.startswith("+"):
            _from = f"+{_from}"
        if not _to.startswith("+"):
            _to = f"+{_to}"
        now = int(time.time() * 1000)
        return {
            "from": _from,
            "to": _to,
            "text": payload["body"],
            "sentStamp": now,
            "receivedStamp": now,
            "battery": payload.get("battery"),
            "power": payload.get("power"),
        }

    raise ValueError(f"unsupported content_type: {webhook.content_type}")
# end of normalize_sms

try:
    conf = Configurator(
        db_path = "/data/webhooks.db",
        ntfy_url = env("NTFY_URL",required=True),
        ntfy_token = env("NTFY_TOKEN",required=True)
    )

    ntfy = Notifier(
        url=conf.ntfy_url,
        token=conf.ntfy_token
    )

    webhook = Webhook.from_env()
    sms = normalize_sms(webhook)
    #     sms={
    #         'from': '+12345678900',
    #         'text': 'This is a measage with\\nnew lines and\\nemojiiis 👨\\u200d🌾👩\\u200d🌾👨\\u200d⚖️',
    #         'sentStamp': 1782239238000,
    #         'receivedStamp': 1782239239557,
    #         'battery': '33',
    #         'power': 'unplugged'  # or "ac"
    #     })

    # n = Notification(
    #     sequence_id=f"{sms['from'].lstrip('+')}-{sms['sentStamp']}",  # idempotency against retries
    #     topic="comms",
    #     message=f"From `{sms['from']}` to `{sms['to']}`\n> {sms['text']}",
    #     # no title
    #     markdown=True,
    #     icon="",  # URL to chat bubble or something
    #     tags=[f"sent:relative_seconds", f"battery:{sms['battery']}", f"power:{sms['power']}"]
    #     # default priority
    #     # no attachments
    #     # no click
    #     # no actions, need ideas
    #     # call? idk
    # )

    n = Notification(
          sequence_id=f"{sms['from'].lstrip('+')}-{sms['sentStamp']}",
          topic="comms",
          message=f"From `{sms['from']}` to `{sms.get('to', 'unknown')}`\n> {sms['text']}",
          markdown=True,
          icon="",
          tags=[t for t in [
              "sent:relative_seconds",
              f"battery:{sms['battery']}" if sms.get("battery") is not None else None,
              f"power:{sms['power']}"     if sms.get("power")   is not None else None,
          ] if t is not None],
          call= "yes" if sms["text"].strip().lower().startswith("/call") else ""
      )
    
    ntfy.post(n)

except ValueError as e:
    print(e)
    sys.exit(200)
except KeyError as e:
    print(f"notify: SMS webhook missing field: {e}")
    sys.exit(100)
except requests.exceptions.RequestException:
    print("notify: ntfy delivery failed")
    sys.exit(202)
except Exception as e:
    print(f"notify: {e}")
    sys.exit(200)

## example of checking missing fields
# required = {"from", "text", "sentStamp", "receivedStamp", "battery", "power"}
# missing = required - sms.keys()
# if missing:
#     log.error(f"SMS webhook missing fields: {missing}")
#     return  # or whatever your framework expects for a 4xx response



## Later ==================

# 1. VALIDATE FIRST: IS THIS A PROPER SMS MESSAGE?
# if not validate(w):
#     # garbage → drop immediately
#     print("DROP_INVALID_WEBHOOK\n")
#     return

# 2. NORMALIZE: Multiple originators use different formats. Must converge to SMS Type
# msg = {
#     "from": w.payload["from"],
#     "to": w.payload["to"],
#     "message": w.payload["message"],
# }

# 3. CLASSIFY: what type of SMS? An OTP? A spam? A human-type?
# label = classify(msg)

# # 4. PERSIST: store in queue for workers to consume
# persist(msg, label, w.meta)


# EXAMPLE:

# def validate(w) -> bool:
#     # STRICT: reject early, no normalization
#     if w.body is None:
#         return False

#     if not isinstance(w.body, dict):
#         return False

#     required = ("from", "to", "message")
#     return all(k in w.body for k in required)


# def classify(msg: dict) -> str:
#     text = msg["message"].lower()

#     if "otp" in text or "code" in text:
#         return "otp"

#     if "test" in text:
#         return "noise"

#     if "stop" in text or "unsubscribe" in text:
#         return "command"

#     return "human"


# def persist(msg: dict, label: str, meta: dict):
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()

#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS sms_queue (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             payload TEXT NOT NULL,
#             label TEXT NOT NULL,
#             meta TEXT,
#             created_at DATETIME DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     cur.execute(
#         "INSERT INTO sms_queue (payload, label, meta) VALUES (?, ?, ?)",
#         (json.dumps(msg), label, json.dumps(meta)),
#     )

#     conn.commit()
#     conn.close()
