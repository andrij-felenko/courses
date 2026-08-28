# 1. Фільтрувати події перемикання контексту: лише коли наступний процес має PID 1234
echo "next_pid == 1234" > /sys/kernel/tracing/events/sched/sched_switch/filter

# 2. Фільтрувати системний виклик openat: лише коли прапорці містять O_CREAT (0x40) і назва починається не з /tmp
echo "(flags & 0x40) && filename !~ \"/tmp/*\"" > /sys/kernel/tracing/events/syscalls/sys_enter_openat/filter

# 3. Фільтрувати події виділення сторінок пам'яті: лише для викликів з обсягом більше 8 сторінок
echo "order > 3" > /sys/kernel/tracing/events/kmem/mm_page_alloc/filter

# 4. Повне скасування фільтра
echo 0 > /sys/kernel/tracing/events/sched/sched_switch/filter
