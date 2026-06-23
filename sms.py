#!/usr/bin/env python3

import json
from pykit import Logger, Configurator, Webhook


conf = Configurator(
    db_path = "/data/webhooks.db"
)

w = Webhook.from_env()
print(w)
print(f"notify: {w}")
print("notified?")

# 1. VALIDATE FIRST (hard gate)
# if not validate(w):
#     # garbage → drop immediately
#     sys.stderr.write("DROP_INVALID_WEBHOOK\n")
#     return

# 2. NORMALIZE (safe because validated)
# msg = {
#     "from": w.payload["from"],
#     "to": w.payload["to"],
#     "message": w.payload["message"],
# }

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
