# 1. Створення моста на хості
ip link add br0 type bridge
ip link set br0 up
ip addr add 10.0.0.254/24 dev br0

# 2. Створення просторів red та blue
ip netns add red
ip netns add blue

# 3. Створення veth-пар для кожного простору
ip link add veth-red type veth peer name veth-red-br
ip link add veth-blue type veth peer name veth-blue-br

# 4. Приєднання хостових кінців до моста br0
ip link set veth-red-br master br0
ip link set veth-blue-br master br0
ip link set veth-red-br up
ip link set veth-blue-br up

# 5. Переміщення кінців у простори та конфігурація IP
ip link set veth-red netns red
ip netns exec red ip addr add 10.0.0.1/24 dev veth-red
ip netns exec red ip link set veth-red up
ip netns exec red ip link set lo up

ip link set veth-blue netns blue
ip netns exec blue ip addr add 10.0.0.2/24 dev veth-blue
ip netns exec blue ip link set veth-blue up
ip netns exec blue ip link set lo up
