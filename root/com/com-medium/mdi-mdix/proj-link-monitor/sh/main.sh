# Створення двох ізольованих просторів імен
sudo ip netns add ns_server
sudo ip netns add ns_switch

# Створення зв'язаної пари veth
sudo ip link add veth_srv type veth peer name veth_sw

# Переміщення інтерфейсів у відповідні простори
sudo ip link set veth_srv netns ns_server
sudo ip link set veth_sw netns ns_switch

# Налаштування IP-адрес та активація
sudo ip netns exec ns_server ip addr add 192.168.50.1/24 dev veth_srv
sudo ip netns exec ns_server ip link set veth_srv up
sudo ip netns exec ns_switch ip addr add 192.168.50.2/24 dev veth_sw
sudo ip netns exec ns_switch ip link set veth_sw up
