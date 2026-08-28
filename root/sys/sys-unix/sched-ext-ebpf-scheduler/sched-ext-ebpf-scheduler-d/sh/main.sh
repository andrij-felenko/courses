# Перевірка поточного стану планувальника
cat /sys/kernel/sched_ext/state
# Можливі значення: disabled, enabling, enabled, disabling

# Перевірка назви активного BPF-планувальника
cat /sys/kernel/sched_ext/root/ops
# Вивід: simple_fifo_demo

# Скільки завдань ядро відхилило під час вмикання планувальника
cat /sys/kernel/sched_ext/nr_rejected
