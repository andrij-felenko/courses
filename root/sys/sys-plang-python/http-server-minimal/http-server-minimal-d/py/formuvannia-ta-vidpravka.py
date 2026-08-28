def send_http_response(client_sock: socket.socket, status_code: int, reason: str,
                       headers: dict[str, str], body: bytes) -> None:
    headers["content-length"] = str(len(body))
    headers["connection"] = "close"
    
    response_lines = [f"HTTP/1.1 {status_code} {reason}"]
    for key, value in headers.items():
        response_lines.append(f"{key}: {value}")
    response_lines.append("")
    response_lines.append("")
    
    header_block = "\r\n".join(response_lines).encode("iso-8859-1")
    client_sock.sendall(header_block + body)
