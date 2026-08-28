#!/bin/bash
set -e

# 1. Створення ізольованих просторів імен
ip netns add ns_sender
ip netns add ns_router
ip netns add ns_receiver

# 2. Створення віртуальних Ethernet-пар (veth)
ip link add veth_s type veth peer name veth_sr
ip link add veth_r type veth peer name veth_rr

# 3. Розподіл інтерфейсів по просторах імен
ip link set veth_s netns ns_sender
ip link set veth_sr netns ns_router
ip link set veth_rr netns ns_router
ip link set veth_r netns ns_receiver

# 4. Налаштування IP-адресації та маршрутів за замовчуванням
ip -n ns_sender addr add 198.51.100.10/24 dev veth_s
ip -n ns_sender link set veth_s up
ip -n ns_sender link set lo up
ip -n ns_sender route add default via 198.51.100.1

ip -n ns_router addr add 198.51.100.1/24 dev veth_sr
ip -n ns_router addr add 192.0.2.1/24 dev veth_rr
ip -n ns_router link set veth_sr up
ip -n ns_router link set veth_rr up
ip -n ns_router link set lo up

ip -n ns_receiver addr add 192.0.2.50/24 dev veth_r
ip -n ns_receiver link set veth_r up
ip -n ns_receiver link set lo up
ip -n ns_receiver route add default via 192.0.2.1

# 5. Увімкнення одноадресної та багатоадресної маршрутизації в ядрі Linux
ip netns exec ns_router sysctl -w net.ipv4.ip_forward=1
ip netns exec ns_router sysctl -w net.ipv4.conf.all.mc_forwarding=1
ip netns exec ns_router sysctl -w net.ipv4.conf.veth_sr.mc_forwarding=1
ip netns exec ns_router sysctl -w net.ipv4.conf.veth_rr.mc_forwarding=1

# 6. Примусове встановлення протоколу IGMPv3 на всіх вузлах
ip netns exec ns_router sysctl -w net.ipv4.conf.all.force_igmp_version=3
ip netns exec ns_receiver sysctl -w net.ipv4.conf.all.force_igmp_version=3
