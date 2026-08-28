# 1. Створення ізольованих просторів імен
sudo ip netns add client_ns
sudo ip netns add server_ns

# 2. Створення віртуальної пари інтерфейсів veth
sudo ip link add veth-c type veth peer name veth-s
sudo ip link set veth-c netns client_ns
sudo ip link set veth-s netns server_ns

# 3. Налаштування IP-адрес
sudo ip netns exec client_ns ip addr add 10.0.0.1/24 dev veth-c
sudo ip netns exec client_ns ip link set veth-c up

sudo ip netns exec server_ns ip addr add 10.0.0.2/24 dev veth-s
sudo ip netns exec server_ns ip link set veth-s up

# 4. Штучне заниження MTU до 1420 на інтерфейсі сервера
sudo ip netns exec server_ns ip link set dev veth-s mtu 1420

# 5. Симуляція Path MTU Black Hole: блокування генерації ICMP fragmentation needed
sudo ip netns exec server_ns iptables -A OUTPUT -p icmp --icmp-type destination-unreachable -j DROP

# 6. Компіляція та запуск утиліти всередині простору імен клієнта
g++ -std=c++20 -O2 pmtu_probe.cpp -o pmtu_probe
sudo ip netns exec client_ns ./pmtu_probe 10.0.0.2
