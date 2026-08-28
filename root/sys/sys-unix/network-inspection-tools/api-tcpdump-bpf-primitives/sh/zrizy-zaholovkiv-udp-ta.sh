# UDP: довжина дейтаграми перевищує 512 байтів (DNS over UDP ретрансляція)
tcpdump -nn "udp and udp[4:2] > 512"

# ICMP: перехоплення повідомлень Destination Unreachable (Тип 3)
tcpdump -nn "icmp and icmp[0] == 3"

# ICMP: перехоплення повідомлень Time-to-Live Exceeded (Тип 11, Код 0)
tcpdump -nn "icmp and icmp[0] == 11 and icmp[1] == 0"

# ICMP: перехоплення луна-запитів Echo Request (Тип 8)
tcpdump -nn "icmp and icmp[0] == 8"
