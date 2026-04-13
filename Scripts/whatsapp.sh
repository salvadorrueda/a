#!/usr/bin/env bash
# Aquest script obre el Whatsapp al firefox.

set -euo pipefail

firefox "https://web.whatsapp.com/"  >/dev/null 2>&1 &
