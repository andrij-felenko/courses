# Перевірка жорсткого ліміту пам'яті (512 МіБ = 536870912 байтів)
cat /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/custom-app-worker.scope/memory.max
# Вивід: 536870912

# Перевірка обмеження кількості задач (64)
cat /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/custom-app-worker.scope/pids.max
# Вивід: 64

# Перевірка списку процесів у групі
cat /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/custom-app-worker.scope/cgroup.procs
# Вивід містить PID запущеного процесу
