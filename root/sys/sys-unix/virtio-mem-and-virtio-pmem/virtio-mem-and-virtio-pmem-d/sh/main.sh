# Скільки пам'яті гість має зараз (базові 4 ГБ + 4 ГБ підключених)
$ grep MemTotal /proc/meminfo
MemTotal:        8388608 kB

# Системні блоки пам'яті, через які драйвер завів суб-блоки
$ lsmem --output RANGE,SIZE,STATE,ZONES
RANGE                                  SIZE  STATE   ZONES
0x0000000100000000-0x00000001ffffffff    4G  online  Movable

# Стан окремого блоку
$ cat /sys/devices/system/memory/memory42/state
online
