#!/bin/bash
# Typora custom command wrapper script
# Usage: ./fetch_and_replace.sh "<selected_url>"

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

# Call Python script to fetch paper information
# Using default mode (Semantic Scholar with automatic fallback to Google Scholar)
python3 "$PYTHON_SCRIPT" "$URL" 2>/dev/null || python "$PYTHON_SCRIPT" "$URL"