#!/usr/bin/env bash

echo "Checking for SSL cert..."

FILE="/etc/letsencrypt/live/comics/fullchain.pem"

if [ -f "$FILE" ]; then
    echo "SSL cert found, starting nginx with HTTPS handling"
    nginx -g "pid /tmp/nginx.pid; daemon off;" -c /opt/django/deploy/nginx-ssl.conf
else
    echo "SSL cert NOT found, starting nginx without HTTPS handling"
    nginx -g "pid /tmp/nginx.pid; daemon off;" -c /opt/django/deploy/nginx.conf
fi