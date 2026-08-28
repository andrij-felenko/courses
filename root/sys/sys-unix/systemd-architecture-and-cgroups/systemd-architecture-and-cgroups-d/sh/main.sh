# 1. Перегляд рекурсивного дерева cgroups та прикріплених процесів
systemd-cgls

# 2. Моніторинг використання CPU, Memory та IO у реальному часі (аналог top)
systemd-cgtop

# 3. Динамічне встановлення ліміту пам'яті для запущеної служби на льоту
systemctl set-property nginx.service MemoryMax=2G CPUWeight=300

# 4. Перевірка приналежності конкретного PID до cgroup у vfs
cat /proc/1420/cgroup

# 5. Інспекція згенерованих файлів обмежень cgroups v2 у /sys/fs
cat /sys/fs/cgroup/system.slice/nginx.service/memory.max
cat /sys/fs/cgroup/system.slice/nginx.service/cpu.weight
