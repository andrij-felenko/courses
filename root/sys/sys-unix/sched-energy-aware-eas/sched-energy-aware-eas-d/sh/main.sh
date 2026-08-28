# Перевірка наявності доменів енергетичної моделі
$ ls /sys/kernel/debug/energy_model/
cpu0  cpu4

# Огляд таблиці OPP для енергоефективного кластера cpu0
$ cat /sys/kernel/debug/energy_model/cpu0/ps:*
# frequency    power    cost    performance
  300000       45       461     100
  600000       95       486     200
  1200000      210      538     400
