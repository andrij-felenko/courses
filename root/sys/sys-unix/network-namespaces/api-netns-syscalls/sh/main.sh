# 1. Створення простору (unshare(CLONE_NEWNET) + mount(MS_BIND) у /var/run/netns/red)
ip netns add red

# 2. Сканування каталогів /var/run/netns/ для виводу списку активних просторів
ip netns list

# 3. Переміщення veth1 у простір (сокет AF_NETLINK, RTM_NEWLINK з атрибутом IFLA_NET_NS_FD)
ip link set veth1 netns red

# 4. Виконання команди (open(/var/run/netns/red) + setns(fd, CLONE_NEWNET) + execvp())
ip netns exec red ip link set lo up

# 5. Видалення простору (umount(/var/run/netns/red) && unlink(/var/run/netns/red))
ip netns del red
