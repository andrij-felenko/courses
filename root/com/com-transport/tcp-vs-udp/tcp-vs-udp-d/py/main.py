import socket

# надійно (TCP): потоковий сокет, кожен байт дійде по порядку
t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
t.connect((server_ip, 1883))
t.sendall(command)                  # з'єднання й повтори — усередині

# швидко (UDP): датаграмний сокет, шлеш і не чекаєш
u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
u.sendto(telemetry, (server_ip, port))   # може загубитись — і байдуже
