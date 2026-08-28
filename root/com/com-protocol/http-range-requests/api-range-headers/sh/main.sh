# 1. Перевірка підтримки Accept-Ranges (запит заголовків)
curl -I https://cdn.example.com/video.mp4

# Очікувана відповідь:
# HTTP/2 200
# accept-ranges: bytes
# content-length: 52428800
# etag: "a89bc34-32"

# 2. Запит першого мегабайта (0 - 1048575 включно)
curl -i -H "Range: bytes=0-1048575" https://cdn.example.com/video.mp4

# Очікувана відповідь:
# HTTP/2 206
# content-range: bytes 0-1048575/52428800
# content-length: 1048576

# 3. Умовне докачування з правильним ETag (повертає 206)
curl -i -H "Range: bytes=1048576-" -H 'If-Range: "a89bc34-32"' https://cdn.example.com/video.mp4

# 4. Умовне докачування зі застарілим ETag (сервер повертає 200 і повний файл)
curl -i -H "Range: bytes=1048576-" -H 'If-Range: "outdated-etag"' https://cdn.example.com/video.mp4

# 5. Тест виходу за межі файлу (повертає 416 Range Not Satisfiable)
curl -i -H "Range: bytes=999999999-1000000000" https://cdn.example.com/video.mp4

# Очікувана відповідь:
# HTTP/2 416
# content-range: bytes */52428800
# content-length: 0
