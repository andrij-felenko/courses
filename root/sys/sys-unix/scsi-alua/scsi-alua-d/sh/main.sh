# Перевірка поточного стану порту
$ cat /sys/class/scsi_disk/2:0:0:0/device/alua_access_state
optimized

# Перевірка ідентифікатора групи TPG
$ cat /sys/class/scsi_disk/2:0:0:0/device/alua_tpg_id
1

# Перевірка підтримуваного типу перемикання
$ cat /sys/class/scsi_disk/2:0:0:0/device/alua_access_type
both
