# Завантаження модуля ядра Linux
modprobe dummy

# Створення виділеного Anycast-інтерфейсу dummy0
ip link add dummy0 type dummy

# Призначення віртуальних адрес Anycast (/32 для IPv4 та /128 для IPv6)
ip addr add 198.51.100.1/32 dev dummy0
ip -6 addr add 2001:db8:any::1/128 dev dummy0

# Активація інтерфейсу
ip link set dummy0 up
