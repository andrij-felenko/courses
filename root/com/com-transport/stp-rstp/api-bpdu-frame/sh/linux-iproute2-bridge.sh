# Створення мосту L2
ip link add name br0 type bridge

# Додавання фізичних інтерфейсів до мосту
ip link set dev eth0 master br0
ip link set dev eth1 master br0

# Увімкнення STP на мосту
ip link set dev br0 type bridge stp_state 1

# Встановлення пріоритету мосту (4096)
ip link set dev br0 type bridge priority 4096

# Перевірка стану STP у Linux
bridge stp show br0
