$ sudo insmod dzherelo.ko
$ dmesg | tail -2
[  894.512700] dzherelo dzherelo: джерело готове
[  894.512884] termo termodatchyk: прив'язано, початок 30000 мК
$ sudo cat /sys/kernel/debug/devices_deferred
$ ls -l /sys/devices/platform/termodatchyk/driver
lrwxrwxrwx 1 root root 0 ... driver -> ../../../bus/platform/drivers/termo
$ ls /sys/bus/platform/drivers/termo/
bind  termodatchyk  uevent  unbind
$ cat /sys/class/hwmon/hwmon4/name
termodatchyk
$ cat /sys/class/hwmon/hwmon4/temp1_input
30100
