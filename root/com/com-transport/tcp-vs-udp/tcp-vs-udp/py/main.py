import socket

# надійно (TCP): кожен байт дійде, по порядку
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.connect((server_ip, 1883))
tcp.sendall(command)           # з'єднання й повтори — усередині

# швидко (UDP): шлеш і не чекаєш
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.sendto(telemetry, (server_ip, port))  # може загубитись — і байдуже
