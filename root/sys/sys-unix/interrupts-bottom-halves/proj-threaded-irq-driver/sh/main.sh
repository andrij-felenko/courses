$ sudo insmod davach.ko
$ sudo cat /dev/davach
174.312004518 -1218
174.313004518 -1187
...
$ grep davach /proc/interrupts
 55:    1042      0      0      0  pinctrl-bcm2835  17 Level  davach
$ ps -eo pid,cls,rtprio,comm | grep irq/55
 312 FF      50 irq/55-davach
$ cat /sys/bus/i2c/devices/1-0048/stats
усього 8336, викинуто 0, від -1904 до 1877
