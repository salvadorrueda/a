#!/usr/bin/env bash
# Aquest script obre Ieduca de INS camí de mar al google-chrome.
set -euo pipefail

google-chrome "https://login.ieduca.com/?error=login.no_token&lang=ca&centre=inscamidemar" >/dev/null 2>&1 &
