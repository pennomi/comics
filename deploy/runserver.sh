#!/usr/bin/env bash

nginx
supervisord -n -c /etc/supervisor/supervisord.conf
