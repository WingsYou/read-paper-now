#!/bin/bash
# Typora 自定义命令包装脚本
# 用法: ./fetch_and_replace.sh "<selected_url>"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/../fetch_paper_info.py"

# 从输入中提取 URL（如果是 markdown 链接格式）
URL="$1"

# 检查是否是 markdown 链接格式 [text](url)
if [[ "$URL" =~ \[.*\]\((.*)\) ]]; then
    URL="${BASH_REMATCH[1]}"
fi

# 去除前后空格
URL=$(echo "$URL" | xargs)

# 调用 Python 脚本获取论文信息
python3 "$PYTHON_SCRIPT" "$URL" 2>/dev/null || python "$PYTHON_SCRIPT" "$URL"
