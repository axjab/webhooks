#!/usr/bin/env python3

import sys, os, requests, time, random
from pykit import Configurator, Webhook, Notifier, Notification, env

with open("/tmp/debug.txt", "a") as f:
    f.write("TRIGGERED\n")

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

    # TEST 1: GET JSON PAYLOAD
    data = sys.argv[1] if len(sys.argv) > 1 else ""  # sucess!

    # TEST 2: GET HEADER/PARAM/FORM PAYLOAD

    headers = f"""
        hookd_id: {os.environ['hook_id']}
        x_forwarded_for: {os.environ['x_forwarded_for']}
        user-agent: {os.environ['user_agent']}
        CONTENT-TYPE: {os.environ['content_type']}
    """
    # headers = ""

    # parameters
    param = f"source: {os.environ['source']}\n"
    # param=""

    # x-www-url-formencoded
    text = f"""\
    message_sid = {os.getenv("message_sid", "")}
    sms_message_sid = {os.getenv("sms_message_sid", "")}
    sms_sid = {os.getenv("sms_sid", "")}
    sms_status = {os.getenv("sms_status", "")}
    from_country = {os.getenv("from_country", "")}
    from_state = {os.getenv("from_state", "")}
    from_city = {os.getenv("from_city", "")}
    from_zip = {os.getenv("from_zip", "")}
    to = {os.getenv("to", "")}
    body = {os.getenv("body", "")}
    """

#################    
    intercepted_response = ntfy.post(
        Notification(
          sequence_id=f"{random.randint(1, 100)}",
          topic="system",
          message=f"{headers}{param}{text}JSON: {data}",
      )
    )

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
