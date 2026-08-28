import socket

def udp_echo():
    # 1) створити UDP-сокет: AF_INET — IPv4, SOCK_DGRAM — датаграми (UDP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 2) закріпити сокет за портом 3333 на всіх інтерфейсах пристрою
    sock.bind(("", 3333))  # порожній рядок — слухати на будь-якій адресі

    while True:
        # 3) чекати датаграму; recvfrom заразом віддає адресу відправника
        data, addr = sock.recvfrom(128)
        if not data:
            break

        print(f"прийнято {len(data)} байтів: {data.decode()}")

        # 4) відіслати ту саму порцію назад — туди, звідки прийшла
        sock.sendto(data, addr)

    sock.close()
