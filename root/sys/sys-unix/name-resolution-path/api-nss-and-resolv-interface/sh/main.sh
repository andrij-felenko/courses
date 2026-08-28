# Перегляд поточного стану DNS-серверів та доменів маршрутизації для всіх інтерфейсів:
resolvectl status

# Запит розв'язання імені через D-Bus API systemd-resolved:
resolvectl query example.com

# Зворотне розв'язання IP-адреси (Reverse DNS Lookup):
resolvectl query 1.1.1.1

# Очищення системного кaшу DNS-відповідей systemd-resolved:
resolvectl flush-caches

# Перегляд статистики влучань у кеш та перевірок DNSSEC:
resolvectl statistics

# Примусове призначення DNS-серверів для конкретного інтерфейсу eth0:
sudo resolvectl dns eth0 1.1.1.1 8.8.8.8

# Налаштування домену маршрутизації (Split-DNS) для VPN-інтерфейсу wg0:
sudo resolvectl domain wg0 "~corp.example.com"
