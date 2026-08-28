# Увімкнення VLAN Filtering на мості br0
sudo ip link set dev br0 type bridge vlan_filtering 1

# Налаштування порту eth1 як Access Port у VLAN 10 (PVID 10, вихід без тегу)
sudo bridge vlan del dev eth1 vid 1
sudo bridge vlan add dev eth1 vid 10 pvid untagged

# Налаштування порту eth2 як Trunk Port (пропускає теговані VLAN 10, 20 та 30)
sudo bridge vlan del dev eth2 vid 1
sudo bridge vlan add dev eth2 vid 10
sudo bridge vlan add dev eth2 vid 20
sudo bridge vlan add dev eth2 vid 30
