# Створення простору імен
sudo ip netns add ns-app

# Переміщення інтерфейсу
sudo ip link set macvlan0 netns ns-app

# Конфігурація IP-адреси всередині ns-app
sudo ip netns exec ns-app ip link set lo up
sudo ip netns exec ns-app ip link set macvlan0 up
sudo ip netns exec ns-app ip addr add 192.168.1.150/24 dev macvlan0
sudo ip netns exec ns-app ip route add default via 192.168.1.1
