def streaming_file_app(environ: dict, start_response):
    """Приклад генератора потокової відповіді з гарантованим закриттям ресурсу."""
    file_handle = open("telemetry_archive.log", "rb")

    def file_stream():
        try:
            while chunk := file_handle.read(65536):
                yield chunk
        finally:
            file_handle.close()

    status = "200 OK"
    headers = [
        ("Content-Type", "application/octet-stream"),
        ("Content-Disposition", "attachment; filename=archive.log"),
    ]
    start_response(status, headers)
    return file_stream()
