# 1. Пошук TCP-з'єднань з нульовим розміром вікна прийому (Zero Window Freeze)
tcpdump -i eth0 -nn "tcp and tcp[14:2] == 0"

# 2. Виявлення переповнення MTU та спроб фрагментації (пакети більше 1500 байтів)
tcpdump -i eth0 -nn "ip and ip[2:2] > 1500"

# 3. Виявлення повторних передач SYN (SYN retransmissions при недоступності сервісу)
tcpdump -i eth0 -nn "tcp[tcpflags] & (tcp-syn) != 0 and tcp[tcpflags] & (tcp-ack) == 0"

# 4. Виявлення штормів RST-пакетів від локального сервера
tcpdump -i eth0 -nn "src host 192.168.1.50 and tcp[tcpflags] & (tcp-rst) != 0"

# 5. Моніторинг відповідей DNS із прапорцем помилки Server Failure (SERVFAIL / NXDOMAIN)
tcpdump -i eth0 -nn "udp src port 53 and (udp[11] & 0x0f != 0)"
