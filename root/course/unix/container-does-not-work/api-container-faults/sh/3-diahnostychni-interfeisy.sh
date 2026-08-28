# Отримання PID головного процесу контейнера на хості
CONTAINER_PID=$(docker inspect --format '{{.State.Pid}}' my-container)

# 1. Перевірка мережевих інтерфейсів та IP-адрес усередині простору контейнера
nsenter -t $CONTAINER_PID -n ip -4 addr show

# 2. Перевірка таблиці маршрутизації контейнера
nsenter -t $CONTAINER_PID -n ip route show

# 3. Перевірка конфігурації резолвера та тестування вбудованого DNS
nsenter -t $CONTAINER_PID -n cat /etc/resolv.conf
nsenter -t $CONTAINER_PID -n dig @127.0.0.11 target-service.my-net +short

# 4. Інспекція правил трансляції адрес DNS (iptables NAT) у просторі контейнера
nsenter -t $CONTAINER_PID -n iptables -t nat -L -n -v
# Типовий ланцюжок перехоплення DNS Docker:
# Chain DOCKER_OUTPUT (1 references)
# pkts bytes target     prot opt in     out     source      destination
#    4   260 DNAT       udp  --  *      *       0.0.0.0/0   127.0.0.11   udp dpt:53 to:127.0.0.11:39451
#    0     0 DNAT       tcp  --  *      *       0.0.0.0/0   127.0.0.11   tcp dpt:53 to:127.0.0.11:41253
