def simple_wsgi_application(environ: dict, start_response) -> list[bytes]:
    status = "200 OK"
    response_headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Cache-Control", "no-cache"),
    ]
    
    # Викликаємо функцію реєстрації статусу та заголовків
    start_response(status, response_headers)
    
    # Повертаємо тіло як список байтових фрагментів
    return [b'{"engine": "WSGI PEP 3333", "status": "ready"}']
