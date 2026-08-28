# 1. Створення clsact qdisc на eth0
tc qdisc add dev eth0 clsact

# 2. Прикріплення eBPF програми до ingress
tc filter add dev eth0 ingress bpf da obj my_prog.o sec classifier

# 3. Перегляд прикріплених BPF фільтрів
tc filter show dev eth0 ingress

# 4. Видалення фільтра або clsact qdisc
tc filter del dev eth0 ingress pref 49152
tc qdisc del dev eth0 clsact
