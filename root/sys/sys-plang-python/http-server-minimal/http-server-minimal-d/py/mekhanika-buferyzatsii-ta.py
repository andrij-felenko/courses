import socket

def read_http_headers(client_sock: socket.socket) -> tuple[bytes, bytes]:
    """Вичитує двійкові дані із сокета до виявлення роздільника \\r\\n\\r\\n.
    
    Повертає кортеж із двох елементів:
      1. header_bytes — сирий двійковий блок стартового рядка та заголовків;
      2. rest_body — залишок байтів, прочитаних у буфер понад заголовки.
    """
    buffer = bytearray()
    delimiter = b"\r\n\r\n"
    max_header_size = 65536  # Захист від вичерпання пам'яті завеликими заголовками
    
    while True:
        pos = buffer.find(delimiter)
        if pos != -1:
            header_bytes = bytes(buffer[:pos])
            rest_body = bytes(buffer[pos + len(delimiter):])
            return header_bytes, rest_body
        
        if len(buffer) >= max_header_size:
            raise ValueError("Розмір заголовків HTTP перевищує дозволений ліміт 64 КБ")
            
        chunk = client_sock.recv(4096)
        if not chunk:
            # Якщо клієнт закрив сокет (EOF), не передавши CRLF CRLF, запит некоректний
            raise ConnectionResetError("Клієнт розірвав з'єднання до завершення передачі заголовків")
        buffer.extend(chunk)
