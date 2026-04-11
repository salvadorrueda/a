#!/usr/bin/env bash
# Aquest script obre l'agenda de GoogleDocs al firefox.

set -euo pipefail

firefox "https://docs.google.com/document/d/1_hzACwwooh4jYHiQvnZ_r4U2j6QmwMPOyFpEE-gKjho/edit?usp=sharing" >/dev/null 2>&1 &
