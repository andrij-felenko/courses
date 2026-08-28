# Перевірка стану блоків пам'яті, створених virtio-mem
$ cat /sys/devices/system/memory/memory42/state
online

# Які зони допустимі для цього блоку
$ cat /sys/devices/system/memory/memory42/valid_zones
Normal Movable

# Чи вважає ядро, що блок можна перевести в offline
$ cat /sys/devices/system/memory/memory42/removable
1
