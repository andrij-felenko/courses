# Перегляд налаштованих адрес та їхніх статусів (preferred, tentative, dynamic):
ip -6 address show dev eth0

# Перегляд кешу сусідів (NDP Neighbor Table) та їхніх станів NUD:
ip -6 neighbour show

# Додавання статичного маршруту через Link-Local Next-Hop:
sudo ip -6 route add 2001:db8:50::/64 via fe80::1 dev eth0

# Зондування сусіднього вузла за протоколом NDP:
sudo ndisc6 2001:db8:1::42 eth0

# Відправлення запиту Router Solicitation до маршрутизаторів:
sudo rdisc6 eth0
