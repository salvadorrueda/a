#!/usr/bin/env bash
set -euo pipefail

exec ssh -t u01.local sudo systemctl poweroff
