import socket

def tcp_client():
    # 1) створити TCP-сокет: SOCK_STREAM — надійний потік байтів (TCP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 2-3) під'єднатися до сервера — тут проходить рукостискання TCP
    sock.connect(("192.168.1.20", 4000))  # адреса й порт сервера

    # 4) надіслати запит — адресу повторювати не треба, вона в з'єднанні
    sock.send(b"STATUS?\n")

    # 5) прочитати відповідь; recv віддає рівно стільки, скільки вже прийшло
    data = sock.recv(256)
    if data:
        print(f"відповідь сервера: {data.decode()}")

    sock.close()  # коректно закрити з'єднання
