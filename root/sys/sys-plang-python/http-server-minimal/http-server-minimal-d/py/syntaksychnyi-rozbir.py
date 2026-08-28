def parse_http_request(header_bytes: bytes) -> tuple[str, str, str, dict[str, str]]:
    text = header_bytes.decode("iso-8859-1")
    lines = text.split("\r\n")
    if not lines or not lines[0]:
        raise ValueError("Порожній HTTP-запит")
    
    # Синтаксичний аналіз стартового рядка
    request_line = lines[0].strip()
    parts = request_line.split(" ")
    if len(parts) != 3:
        raise ValueError(f"Некоректний формат стартового рядка: '{request_line}'")
    
    method, path, version = parts
    
    # Синтаксичний аналіз заголовків
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if not line:
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()
        
    return method, path, version, headers
