#!/bin/bash

PAYLOAD='{"from":"+111111","to":"+22222","message":"test otp code"}'

hook_id=1 \
hook_name=sms \
hook_method=POST \
x_forwarded_for=127.0.0.1 \
user_agent=dev \
content_type=application/json \
uv run sms.py "$PAYLOAD"
