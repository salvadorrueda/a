#!/usr/bin/env bash
set -euo pipefail

exec ssh -t d00.local sudo systemctl poweroff
