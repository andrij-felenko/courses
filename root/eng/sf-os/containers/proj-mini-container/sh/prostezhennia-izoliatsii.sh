# Перевірка PID: ми бачимо лише наш шелл як PID 1
/ # ps aux
PID   USER     TIME  COMMAND
    1 root      0:00 /bin/sh
    5 root      0:00 ps aux

# Перевірка імені хоста
/ # hostname
minicontainer

# Перевірка обмеження пам'яті через cgroups v2
/ # cat /sys/fs/cgroup/memory.max
268435456

# Спроба виконати заборонену дію (скинутий CAP_SYS_ADMIN)
/ # mount -t tmpfs none /mnt
mount: permission denied (are you root?)
