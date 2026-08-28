# Налаштовуємо порт veth-b1-br для клієнта Blue (VLAN 10 Access)
sudo bridge vlan del dev veth-b1-br vid 1
sudo bridge vlan add dev veth-b1-br vid 10 pvid untagged

# Налаштовуємо порт veth-b2-br для клієнта Blue (VLAN 10 Access)
sudo bridge vlan del dev veth-b2-br vid 1
sudo bridge vlan add dev veth-b2-br vid 10 pvid untagged

# Налаштовуємо порт veth-r1-br для клієнта Red (VLAN 20 Access)
sudo bridge vlan del dev veth-r1-br vid 1
sudo bridge vlan add dev veth-r1-br vid 20 pvid untagged
