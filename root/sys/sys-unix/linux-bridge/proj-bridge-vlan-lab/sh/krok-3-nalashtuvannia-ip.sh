# Налаштовуємо ns-blue1 (VLAN 10, вузол 1)
sudo ip -n ns-blue1 link set lo up
sudo ip -n ns-blue1 link set dev veth-b1 name eth0
sudo ip -n ns-blue1 addr add 192.168.10.1/24 dev eth0
sudo ip -n ns-blue1 link set dev eth0 up

# Налаштовуємо ns-blue2 (VLAN 10, вузол 2)
sudo ip -n ns-blue2 link set lo up
sudo ip -n ns-blue2 link set dev veth-b2 name eth0
sudo ip -n ns-blue2 addr add 192.168.10.2/24 dev eth0
sudo ip -n ns-blue2 link set dev eth0 up

# Налаштовуємо ns-red1 (VLAN 20, вузол 1)
sudo ip -n ns-red1 link set lo up
sudo ip -n ns-red1 link set dev veth-r1 name eth0
sudo ip -n ns-red1 addr add 192.168.20.1/24 dev eth0
sudo ip -n ns-red1 link set dev eth0 up
