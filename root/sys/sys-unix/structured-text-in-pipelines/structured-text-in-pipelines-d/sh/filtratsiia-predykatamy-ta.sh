# Фільтрація помилок сервера та створення нового об'єкта
curl -s https://api.example.com/events | jq '
  .events[]
  | select(.status >= 500 and .latency_ms > 1000)
  | {
      timestamp: .ts,
      endpoint: .path,
      error_code: .status,
      duration_sec: (.latency_ms / 1000)
    }
'
