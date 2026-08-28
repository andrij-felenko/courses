def stream_large_file(file_path: str):
    with open(file_path, "rb") as f:
        while chunk := f.read(65536): # Читання блоками по 64 КБ
            yield chunk

# Відправлення гігабайтного файлу без виділення гігабайта в RAM
response = requests.post(
    "https://storage.example.com/upload",
    data=stream_large_file("/var/backups/db.dump")
)
