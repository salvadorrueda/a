#!/usr/bin/env bash
set -euo pipefail

exec ssh -t vu01.local sudo systemctl poweroff