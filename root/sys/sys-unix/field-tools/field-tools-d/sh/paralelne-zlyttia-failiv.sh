# Створення тестових файлів
printf "host1\nhost2\nhost3\n" > hosts.txt
printf "192.168.1.10\n192.168.1.11\n192.168.1.12\n" > ips.txt

# Горизонтальне склеювання через кому
paste -d, hosts.txt ips.txt
# Вивід:
# host1,192.168.1.10
# host2,192.168.1.11
# host3,192.168.1.12
