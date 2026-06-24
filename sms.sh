#!/bin/bash

exec >> /tmp/webhookd.log 2>&1

hook_method="$hook_method" \
hook_name="$hook_name" \
hook_id="$hook_id" \
x_forwarded_for="$x_forwarded_for" \
user_agent="$user_agent" \
x_webauth_user="${x_webauth_user:-anon}" \
content_type="${content_type:-text/plain}" \
data="${1:-}" \
"$WHD_HOOK_SCRIPTS"/sms.py

# DOCUMENTATION ON Input Handling:

# Webhookd automatically converts various incoming request data into script variables:

# Query Parameters: Converted directly to script variables.
# HTTP Headers: Converted, following the snake_case convention. (e.g., CONTENT-TYPE becomes content_type).
# Request Body:
# application/x-www-form-urlencoded: Keys/values are mapped to variables.
# text/* or application/json: The entire payload is passed as the first script parameter ($1).
# Built-in Parameters Added by Webhookd:

# Variable	Description
# hook_id	Unique hook ID (auto-increment)
# hook_name	Name associated with the webhook call
# hook_method	HTTP request method used
# x_forwarded_for	Client IP address
# x_webauth_user	Username if authentication is enabled
# Example Usage:

# $ curl --data @test.json -H 'Content-Type: application/json' http://localhost:8080/echo?foo=bar
# # Script output shows variables mapped correctly
# Hook information: name=echo, id=1, method=POST
# Query parameter: foo=bar
# Header parameter: user-agent=curl/...
# Script parameters: {"message": "this is a test"}

# SAMPLE
# application/json; charset=utf-8
# {
#   "from":"+12345678900",
#   "text":"djdhd\nfdhejdj\ndjdjdf\ndhdjd\n\uD83D\uDC68\u200D\u2696\uFE0F\uD83D\uDC68\u200D\uD83C\uDFED\uD83D\uDC68\u200D\u2696\uFE0F",
#   "sentStamp":1782217557000,
#   "receivedStamp":1782217558438,
#   "battery": "39",
#   "power": "unplugged"  # or "ac" for plugged, are there more?
# }


# echo "=== ${hook_method} /${hook_name}/${hook_id} ==="
# echo "IP: ${x_forwarded_for}"   # aka Host
# echo "originator: ${user_agent}"        # system which triggered request
# echo "user: ${x_webauth_user:-anon}"	# Username if authentication is enabled
# echo $content_type      # text/plain by default
