# 1. Перевірка монтування файлової системи bpffs
mount -t bpf bpf /sys/fs/bpf 2>/dev/null || true

# 2. Завантаження BPF програми в ядро
bpftool prog load monitor_iter.bpf.o /sys/fs/bpf/monitor_prog type tracing

# 3. Створення та закріплення BPF-ітератора
bpftool iter pin /sys/fs/bpf/monitor_prog /sys/fs/bpf/task_inspector

# 4. Закріплення мапи User Ring Buffer для доступу користувацького процесу
bpftool map pin name cmd_ringbuf /sys/fs/bpf/cmd_ringbuf_map
