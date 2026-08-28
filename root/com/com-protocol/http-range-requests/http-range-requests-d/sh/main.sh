# 1. Запит першого мегабайта файлу з відображенням службових заголовків
curl -i -H "Range: bytes=0-1048575" https://cdn.example.com/video.mp4

# 2. Суфіксний запит останніх 512 байтів файлу (читання moov-атома або Parquet footer)
curl -i -H "Range: bytes=-512" https://cdn.example.com/data.parquet

# 3. Перевірка роботи умовного валідатора If-Range (має повернути 206)
curl -i -H "Range: bytes=1000-" -H 'If-Range: "pkg-v1-hash-8a9f"' https://cdn.example.com/archive.zip

# 4. Перевірка спрацьовування захисту від некоректного діапазону (очікується HTTP 416)
curl -i -H "Range: bytes=999999999999-" https://cdn.example.com/small.txt
