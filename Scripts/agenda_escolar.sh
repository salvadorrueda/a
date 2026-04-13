#!/usr/bin/env bash
# Aquest script obre l'agenda escolar al Google Chrome.

set -euo pipefail

google-chrome "https://docs.google.com/document/d/1mo3LupQcUH9-KqcvCA-4-T29K0MokWBTwAgcryFMx5o/edit?tab=t.0" >/dev/null 2>&1 &