#!/usr/bin/env python3

import sys, json
from pykit import Configurator, Webhook, load_webhook


# TODO: NEED A LOGGER

conf = Configurator(
    db_path = "/data/webhooks.db"
)

w : Webhook = load_webhook()
print(w)

print("notify: SMS RECEIVED")  # TODO: TEST THIS: Will be notified
print("\nThis is debug output, will be ignored.")

# 1. VALIDATE FIRST (hard gate)
# if not validate(w):
#     # garbage → drop immediately
#     sys.stderr.write("DROP_INVALID_WEBHOOK\n")
#     return

# 2. NORMALIZE (safe because validated)
msg = {
    "from": w.body["from"],
    "to": w.body["to"],
    "message": w.body["message"],
}

# 3. CLASSIFY
# label = classify(msg)

# # 4. PERSIST
# persist(msg, label, w.meta)

def validate(w) -> bool:
    # STRICT: reject early, no normalization
    if w.body is None:
        return False

    if not isinstance(w.body, dict):
        return False

    required = ("from", "to", "message")
    return all(k in w.body for k in required)


def classify(msg: dict) -> str:
    text = msg["message"].lower()

    if "otp" in text or "code" in text:
        return "otp"

    if "test" in text:
        return "noise"

    if "stop" in text or "unsubscribe" in text:
        return "command"

    return "human"


def persist(msg: dict, label: str, meta: dict):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sms_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload TEXT NOT NULL,
            label TEXT NOT NULL,
            meta TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute(
        "INSERT INTO sms_queue (payload, label, meta) VALUES (?, ?, ?)",
        (json.dumps(msg), label, json.dumps(meta)),
    )

    conn.commit()
    conn.close()
