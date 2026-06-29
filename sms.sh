#!/bin/bash

exec >> /tmp/webhookd.log 2>&1

main() {
	hook_method="$hook_method" \
	hook_name="$hook_name" \
	hook_id="$hook_id" \
	x_forwarded_for="$x_forwarded_for" \
	user_agent="$user_agent" \
	x_webauth_user="${x_webauth_user:-anon}" \
	content_type="${content_type:-text/plain}" \
	payload=$(fetch_payload "$1") \
	"$WHD_HOOK_SCRIPTS"/sms.py
}

fetch_payload() {
    case "$content_type" in
        *application/json*)
        	payload="$1" ;;
        *application/x-www-form-urlencoded*) 
            payload=$(route_by_source "$source") ;;
    esac
    echo "$payload"
}

route_by_source() {
    case "$1" in
        twilio)
            payload=$(build_twilio_payload)
    esac
    echo "$payload"
}

build_twilio_payload() {
    echo "{
  \"to_country\": \"$to_country\",
  \"error_url\": \"$error_url\",
  \"to_state\": \"$to_state\",
  \"sms_message_sid\": \"$sms_message_sid\",
  \"error_code\": \"$error_code\",
  \"num_media\": \"$num_media\",
  \"to_city\": \"$to_city\",
  \"from_zip\": \"$from_zip\",
  \"sms_sid\": \"$sms_sid\",
  \"from_state\": \"$from_state\",
  \"sms_status\": \"$sms_status\",
  \"from_city\": \"$from_city\",
  \"body\": \"$body\",
  \"from_country\": \"$from_country\",
  \"to\": \"$to\",
  \"to_zip\": \"$to_zip\",
  \"num_segments\": \"$num_segments\",
  \"message_sid\": \"$message_sid\",
  \"account_sid\": \"$account_sid\",
  \"from\": \"$from\",
  \"api_version\": \"$api_version\"
}"
}

main "$1"

# payload
# application/x-www-form-urlencoded
# 
# notify: name 'payload' is not defined
# payload
# application/json; charset=utf-8
# {
#   "from":"+12362045999",
#   "text":"error: exit status 200",
#   "sentStamp":1782769670000,
#   "receivedStamp":1782769671898,
#   "battery": "52",
#   "power": "unplugged"
# }

# echo "MESSAGE: ToCountry=CA&ErrorUrl=https%3A%2F%2Fnonexistend.cx%2Fhook%2Fsms&ToState=BC&SmsMessageSid=SMfed169349343bead241a7f2c9294f3bc&ErrorCode=11210&NumMedia=0&ToCity=&FromZip=&SmsSid=SMfed169349343bead241a7f2c9294f3bc&FromState=Ontario&SmsStatus=received&FromCity=&Body=rehdhdbd&FromCountry=CA&To=%2B12362045999&ToZip=&NumSegments=1&MessageSid=SMfed169349343bead241a7f2c9294f3bc&AccountSid=AC4b936e28767ae957b91c02fe1a850023&From=%2B13432045999&ApiVersion=2010-04-01"


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
