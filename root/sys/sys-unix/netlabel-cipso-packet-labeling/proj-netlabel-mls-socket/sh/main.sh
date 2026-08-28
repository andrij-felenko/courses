# 1. Створення ізольованих просторів імен для клієнта та сервера
ip netns add ns_server
ip netns add ns_client

# 2. Створення віртуальної пари інтерфейсів
ip link add veth_srv type veth peer name veth_cli
ip link set veth_srv netns ns_server
ip link set veth_cli netns ns_client

# 3. Налаштування IP-адрес та запуск інтерфейсів
ip netns exec ns_server ip addr add 192.168.100.1/24 dev veth_srv
ip netns exec ns_server ip link set veth_srv up
ip netns exec ns_server ip link set lo up

ip netns exec ns_client ip addr add 192.168.100.2/24 dev veth_cli
ip netns exec ns_client ip link set veth_cli up
ip netns exec ns_client ip link set lo up

# 4. Налаштування NetLabel для інтерфейсів у кожному просторі
ip netns exec ns_server netlabelctl cipsov4 add pass doi:1 tags:1
ip netns exec ns_server netlabelctl map add default protocol:cipsov4,1

ip netns exec ns_client netlabelctl cipsov4 add pass doi:1 tags:1
ip netns exec ns_client netlabelctl map add default protocol:cipsov4,1

# 5. Перевірка наявності CIPSO-опцій у мережевому трафіку через tcpdump
# У першому терміналі:
ip netns exec ns_server tcpdump -i veth_srv -vvv -n -X 'ip[20:1] == 0x86'

# 6. Запуск MLS-сервера та відправка тестового запиту від процесу з MLS-міткою
# Запуск сервера:
ip netns exec ns_server ./mls_server &

# Запуск клієнта під керуванням runcon з підвищеним рівнем чутливості s1:c0,c4:
ip netns exec ns_client runcon -l "s1:c0,c4" curl http://192.168.100.1:8443/
