#!/bin/bash
# Typora custom command wrapper script (Google Scholar mode)
# Usage: ./fetch_and_replace_gs.sh "<selected_url>"
# This version prioritizes Google Scholar for more accurate citation counts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/../fetch_paper_info.py"

# Extract URL from input (if it's markdown link format)
URL="$1"

# Check if it's markdown link format [text](url)
if [[ "$URL" =~ \[.*\]\((.*)\) ]]; then
    URL="${BASH_REMATCH[1]}"
fi

# Trim whitespace
URL=$(echo "$URL" | xargs)

# Call Python script with Google Scholar priority
# This provides more accurate and up-to-date citation counts
python3 "$PYTHON_SCRIPT" "$URL" --use-google-scholar-citations 2>/dev/null || \
python "$PYTHON_SCRIPT" "$URL" --use-google-scholar-citations