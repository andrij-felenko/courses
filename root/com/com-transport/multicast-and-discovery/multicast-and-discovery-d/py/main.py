import socket, struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", 5000))

# група + адреса локального інтерфейсу, на якому її слухати
mreq = struct.pack("4s4s", socket.inet_aton("239.1.2.3"),
                           socket.inet_aton("192.168.1.10"))
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
