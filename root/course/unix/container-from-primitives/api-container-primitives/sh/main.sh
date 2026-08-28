# 1. Створення пари віртуальних кабелів
ip link add veth-host type veth peer name veth-guest

# 2. Переміщення кінця кабелю veth-guest у простір імен цільового процесу PID
ip link set veth-guest netns <PID>

# 3. Прив'язка veth-host до хостового мосту br0
ip link set veth-host master br0
ip link set veth-host up

# 4. Налаштування інтерфейсу всередині простору імен контейнера
ip netns exec <ім'я_простору> ip addr add 10.0.0.2/24 dev veth-guest
ip netns exec <ім'я_простору> ip link set veth-guest name eth0
ip netns exec <ім'я_простору> ip link set eth0 up
ip netns exec <ім'я_простору> ip link set lo up
ip netns exec <ім'я_простору> ip route add default via 10.0.0.1
