# Створюємо ізольовані простори імен для орендарів
sudo ip netns add ns-blue1
sudo ip netns add ns-blue2
sudo ip netns add ns-red1

# Створюємо пари віртуальних кабелів veth
sudo ip link add veth-b1 type veth peer name veth-b1-br
sudo ip link add veth-b2 type veth peer name veth-b2-br
sudo ip link add veth-r1 type veth peer name veth-r1-br

# Переносимо клієнтські кінці veth у відповідні простори імен
sudo ip link set veth-b1 netns ns-blue1
sudo ip link set veth-b2 netns ns-blue2
sudo ip link set veth-r1 netns ns-red1

# Приєднуємо хостові кінці veth до моста br-core
sudo ip link set veth-b1-br master br-core
sudo ip link set veth-b2-br master br-core
sudo ip link set veth-r1-br master br-core

# Переводимо хостові інтерфейси в активний стан (UP)
sudo ip link set dev veth-b1-br up
sudo ip link set dev veth-b2-br up
sudo ip link set dev veth-r1-br up
