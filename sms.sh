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
