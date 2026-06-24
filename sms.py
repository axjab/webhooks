#!/usr/bin/env python3

import json
from pykit import Logger, Configurator, Webhook, Notifier, Notification, env


conf = Configurator(
    db_path = "/data/webhooks.db",
    ntfy_url = env("NTFY_URL"),
    ntfy_token = env("NTFY_TOKEN")
)

ntfy = Notifier(
    url=conf.ntfy_url,
    token=conf.ntfy_token
)

w = Webhook.from_env()  # not yet validated
# sample:
# Webhook(
#     id='8',
#     name='sms',
#     method='POST',
#     originator='SMS Forwarder App',
#     x_forwarded_for='209.87.229.73',
#     x_webauth_user='anon',
#     content_type='application/json; charset=utf-8',
#     payload=(sms)

sms = w.payload
#     sms={
#         'from': '+12345678900',
#         'text': 'This is a measage with\\nnew lines and\\nemojiiis 👨\\u200d🌾👩\\u200d🌾👨\\u200d⚖️',
#         'sentStamp': 1782239238000,
#         'receivedStamp': 1782239239557,
#         'battery': '33',
#         'power': 'unplugged'  # or "ac"
#     })

# Clean up and send to ntfy
n = Notification(
    sequence_id=f"sms:{sms['from']}:{sms['sentStamp']}", # idempotency against retries
    topic="sms",
    message=sms["text"],
    title=f"Message from {sms['from']}",  # in the future, this should be matched to contacts from Radicale server
    markdown=False,
    icon="",  # chat bubble or something
    tags=[f"sent:relative_seconds", f"battery:{sms['battery']}", f"power:{sms['power']}"]
    # default priority
    # no attachments
    # no click
    # no actions, need ideas
    # call? idk
)

ntfy.notify(n)


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
