# 1. Виявлення процесів-зомбі та їхніх батьківських ідентифікаторів
ps -eo pid,ppid,pgid,stat,comm | grep -E 'STAT|Z'
# Приклад проблемного дерева:
#   PID  PPID  PGID STAT COMMAND
#     1     0     1 Ss   node
#    45     1     1 Z    python3 <defunct>

# 2. Інспекція маски перехоплення сигналів процесу PID 1 у контейнері
cat /proc/$CONTAINER_PID/status | grep -E 'SigBlk|SigIgn|SigCgt'
# SigBlk: 0000000000000000 (заблоковані сигнали)
# SigIgn: 0000000000000000 (ігноровані сигнали)
# SigCgt: 0000000180004002 (перехоплені сигнали: 16-ткова бітова маска)

# Розшифрування бітової маски за допомогою команди:
# Біт 15 (SIGTERM = 15) повинен бути встановлений у 1 (1 << 14), інакше SIGTERM ігнорується ядром!

# 3. Перевірка споживання ліміту кількості процесів у cgroups v2
cat /sys/fs/cgroup/system.slice/docker-$CONTAINER_ID.scope/pids.current
cat /sys/fs/cgroup/system.slice/docker-$CONTAINER_ID.scope/pids.max
