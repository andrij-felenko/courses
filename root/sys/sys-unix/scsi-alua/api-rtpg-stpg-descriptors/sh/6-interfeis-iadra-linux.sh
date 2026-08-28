# Зчитування поточного стану доступу
$ cat /sys/class/scsi_disk/2:0:0:0/device/alua_access_state
optimized

# Перевірка ідентифікатора групи портів
$ cat /sys/class/scsi_disk/2:0:0:0/device/alua_tpg_id
1

# Перевірка ознаки бажаного контролера (Preferred)
$ cat /sys/class/scsi_disk/2:0:0:0/device/alua_pref
1
