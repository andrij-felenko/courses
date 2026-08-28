# Перевірка фізичної швидкості лінку мережевого адаптера eth0
$ cat /sys/class/net/eth0/speed
1000

# Перевірка статусу підключення кабелю
$ cat /sys/class/net/eth0/operstate
up

# Зміна алгоритму планувальника I/O для накопичувача nvme0n1
$ echo mq-deadline > /sys/block/nvme0n1/queue/scheduler
