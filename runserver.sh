#!/usr/bin/env bash

cd /opt/comics
supervisord -n -c /etc/supervisor/supervisord.conf
