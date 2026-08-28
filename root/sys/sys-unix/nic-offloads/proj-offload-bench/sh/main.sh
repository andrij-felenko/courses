#!/usr/bin/env bash
set -e

# 1. Створення двох просторів імен: client_ns та server_ns
ip netns add client_ns
ip netns add server_ns

# 2. Створення віртуальної пари veth-інтерфейсів veth0 <-> veth1
ip link add veth0 type veth peer name veth1

# 3. Переміщення інтерфейсів у відповідні простори імен
ip link set veth0 netns client_ns
ip link set veth1 netns server_ns

# 4. Налаштування IP-адрес та підняття інтерфейсів
ip netns exec client_ns ip addr add 10.0.0.1/24 dev veth0
ip netns exec client_ns ip link set veth0 up
ip netns exec client_ns ip link set lo up

ip netns exec server_ns ip addr add 10.0.0.2/24 dev veth1
ip netns exec server_ns ip link set veth1 up
ip netns exec server_ns ip link set lo up

echo "Тестове середовище успішно створено!"
echo "Client IP: 10.0.0.1 (veth0 в client_ns)"
echo "Server IP: 10.0.0.2 (veth1 в server_ns)"
