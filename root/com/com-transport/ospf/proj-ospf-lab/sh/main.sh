# Створення просторів імен для трьох вузлів
ip netns add R1
ip netns add R2
ip netns add R3

# Створення з'єднувальних veth-пар
ip link add veth-r1-r2 type veth peer name veth-r2-r1
ip link add veth-r2-r3 type veth peer name veth-r3-r2

# Розподіл інтерфейсів по відповідних просторах імен
ip link set veth-r1-r2 netns R1
ip link set veth-r2-r1 netns R2
ip link set veth-r2-r3 netns R2
ip link set veth-r3-r2 netns R3

# Налаштування IP-адрес на R1
ip netns exec R1 ip addr add 10.0.0.1/30 dev veth-r1-r2
ip netns exec R1 ip link set veth-r1-r2 up
ip netns exec R1 ip link set lo up
ip netns exec R1 ip link add name lo-stub type dummy
ip netns exec R1 ip addr add 192.168.1.1/24 dev lo-stub
ip netns exec R1 ip link set lo-stub up

# Налаштування IP-адрес на R2
ip netns exec R2 ip addr add 10.0.0.2/30 dev veth-r2-r1
ip netns exec R2 ip addr add 10.0.1.1/30 dev veth-r2-r3
ip netns exec R2 ip link set veth-r2-r1 up
ip netns exec R2 ip link set veth-r2-r3 up
ip netns exec R2 ip link set lo up

# Налаштування IP-адрес на R3
ip netns exec R3 ip addr add 10.0.1.2/30 dev veth-r3-r2
ip netns exec R3 ip link set veth-r3-r2 up
ip netns exec R3 ip link set lo up

# Увімкнення IP Forwarding у ядрі для всіх просторів імен
ip netns exec R1 sysctl -w net.ipv4.ip_forward=1
ip netns exec R2 sysctl -w net.ipv4.ip_forward=1
ip netns exec R3 sysctl -w net.ipv4.ip_forward=1
