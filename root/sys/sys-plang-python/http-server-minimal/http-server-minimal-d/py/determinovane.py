def read_http_body(client_sock: socket.socket, rest_body: bytes, content_length: int) -> bytes:
    if len(rest_body) >= content_length:
        return rest_body[:content_length]
    
    body = bytearray(rest_body)
    bytes_remaining = content_length - len(body)
    
    while bytes_remaining > 0:
        chunk = client_sock.recv(min(4096, bytes_remaining))
        if not chunk:
            raise ConnectionResetError("Передчасний обрив TCP-потоку під час читання тіла запиту")
        body.extend(chunk)
        bytes_remaining -= len(chunk)
        
    return bytes(body)
