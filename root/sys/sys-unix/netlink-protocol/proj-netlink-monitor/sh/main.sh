# 1. Створення віртуальної пари інтерфейсів veth0 та veth1
sudo ip link add veth0 type veth peer name veth1

# 2. Призначення IPv4 адреси на інтерфейс veth0
sudo ip addr add 192.168.100.1/24 dev veth0

# 3. Активація інтерфейсу (переведення в стан UP)
sudo ip link set dev veth0 up

# 4. Деактивація та видалення віртуального пристрою
sudo ip link set dev veth0 down
sudo ip link del dev veth0
