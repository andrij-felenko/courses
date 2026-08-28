set -o pipefail

curl -s "https://api.example.com/data.json" \
  | jq -e '.data[] | select(.valid == true)' \
  | gzip -c > output.gz

PIPE_STATUS=("${PIPESTATUS[@]}")
if [ "${PIPE_STATUS[0]}" -ne 0 ] || [ "${PIPE_STATUS[1]}" -ne 0 ]; then
  echo "[CRITICAL] Помилка завантаження або фільтрації JSON" >&2
  exit 1
fi
