# 1. Захоплення виключно пакетів ініціалізації з'єднання (SYN без ACK)
tcpdump -nn "tcp[tcpflags] & (tcp-syn) != 0 and tcp[tcpflags] & (tcp-ack) == 0"

# 2. Відповіді сервера на запити підключення (SYN-ACK)
tcpdump -nn "tcp[tcpflags] & (tcp-syn|tcp-ack) == (tcp-syn|tcp-ack)"

# 3. Виявлення всіх пакетів скидання зв'язку (RST)
tcpdump -nn "tcp[tcpflags] & (tcp-rst) != 0"

# 4. Виявлення пакетів закриття з'єднань (FIN)
tcpdump -nn "tcp[tcpflags] & (tcp-fin) != 0"

# 5. Детекція NULL-сканування портів (усі прапорці дорівнюють нулю)
tcpdump -nn "tcp[tcpflags] == 0"

# 6. Детекція XMAS-сканування (активні прапорці FIN, PSH та URG одночасно)
tcpdump -nn "tcp[tcpflags] & (tcp-fin|tcp-push|tcp-urg) == (tcp-fin|tcp-push|tcp-urg)"

# 7. Детекція SYN-RST аномалій (некоректна комбінація SYN та RST)
tcpdump -nn "tcp[tcpflags] & (tcp-syn|tcp-rst) == (tcp-syn|tcp-rst)"
