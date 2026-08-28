# Увімкнення виявлення MTU без використання ICMP (PLPMTUD, RFC 4821)
# 0 = вимкнено, 1 = вмикається автоматично при виявленні чорної діри, 2 = увімкнено постійно
sudo sysctl -w net.ipv4.tcp_mtu_probing=1

# Базовий розмір MSS при пошуку чорних дір MTU (рекомендовано 1024 або 536 байтів)
sudo sysctl -w net.ipv4.tcp_base_mss=1024

# Дозвіл безпечного повторного використання сокетів у стані TIME_WAIT для вихідних з'єднань NAT
sudo sysctl -w net.ipv4.tcp_tw_reuse=1

# Контроль генерації часових міток TCP (RFC 7323)
# Деякі застарілі фаєрволи блокують пакети зі зміщеними timestamps
sudo sysctl -w net.ipv4.tcp_timestamps=1

# Збільшення максимального розміру таблиці conntrack для уникнення переповнення при SYN-flood
sudo sysctl -w net.netfilter.nf_conntrack_max=1048576

# Зменшення часу утримання стану TCP ESTABLISHED на навантажених шлюзах (замість 5 діб)
sudo sysctl -w net.netfilter.nf_conntrack_tcp_timeout_established=3600
