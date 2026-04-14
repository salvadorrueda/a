#!/usr/bin/env bash
# This script is used to run the code in the "a" directory.

set -euo pipefail

git -C /home/salvadorrueda/Developer/GitHub/a pull

code /home/salvadorrueda/Developer/GitHub/a
