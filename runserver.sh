#!/usr/bin/env bash

cd /opt/django
nginx
supervisord -n -c /etc/supervisor/supervisord.conf
