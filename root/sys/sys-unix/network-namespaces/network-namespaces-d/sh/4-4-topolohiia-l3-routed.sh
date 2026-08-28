# На хості
ip link add veth-c1 type veth peer name veth-guest
ip link set veth-guest netns guest

# Всередині контейнера guest
ip netns exec guest ip addr add 10.1.1.2/32 dev veth-guest
ip netns exec guest ip link set veth-guest up
ip netns exec guest ip route add 169.254.1.1 dev veth-guest
ip netns exec guest ip route add default via 169.254.1.1

# На хості
ip link set veth-c1 up
ip route add 10.1.1.2 dev veth-c1
