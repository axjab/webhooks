#!/bin/bash

echo "hello! $(date)" >> /tmp/webhook.test

echo "notify: Success message for deployment." # Will be notified
echo "This is debug output, will be ignored."  # Will not trigger notification
