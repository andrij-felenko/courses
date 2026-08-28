# Перевірка PID (має бути PID 1)
ps aux
# PID   USER     TIME  COMMAND
#     1 root      0:00 /bin/sh

# Перевірка імені хоста
hostname
# minibox

# Перевірка обмеження пам'яті
cat /sys/fs/cgroup/memory.max
# 67108864

# Перевірка блокування системних викликів фільтром seccomp
reboot
# reboot: Operation not permitted
