# 1. Створення пари віртуальних інтерфейсів на хості
sudo ip link add veth_host type veth peer name veth_guest

# 2. Переміщення кінця veth_guest у мережевий простір дочірнього процесу
sudo ip link set veth_guest netns <child_pid>

# 3. Налаштування хостового кінця інтерфейсу
sudo ip addr add 10.200.1.1/24 dev veth_host
sudo ip link set veth_host up

# 4. Налаштування інтерфейсу всередині простору назв контейнера
sudo nsenter -t <child_pid> -n ip addr add 10.200.1.2/24 dev veth_guest
sudo nsenter -t <child_pid> -n ip link set dev veth_guest name eth0
sudo nsenter -t <child_pid> -n ip link set eth0 up
sudo nsenter -t <child_pid> -n ip link set lo up
sudo nsenter -t <child_pid> -n ip route add default via 10.200.1.1
