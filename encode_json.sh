#!/bin/bash

JSON_FILE="vidlab-marketing-460409-f0e918ae72e2.json"
OUTPUT_FILE="encoded.txt"

if [ ! -f "$JSON_FILE" ]; then
  echo "❌ 找不到 $JSON_FILE"
  exit 1
fi

base64 "$JSON_FILE" > "$OUTPUT_FILE"
echo "✅ 成功转成 base64，结果储存在 $OUTPUT_FILE"
echo "🚀 把 encoded.txt 的内容 copy 去 Render.com 的环境变量：CREDENTIAL_JSON"
