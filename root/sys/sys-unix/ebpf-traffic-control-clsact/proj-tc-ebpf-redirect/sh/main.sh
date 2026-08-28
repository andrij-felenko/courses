# Перевірка наявності qdisc clsact на veth0
tc qdisc show dev veth0

# Перевірка прикріпленого BPF фільтра та його ID
tc filter show dev veth0 ingress

# Інспекція всіх завантажених BPF програм у системі через bpftool
sudo bpftool net show
sudo bpftool prog show type sched_cls

# Перегляд логів bpf_trace_printk (якщо додано налагоджувальний вивід)
sudo cat /sys/kernel/debug/tracing/trace_pipe
