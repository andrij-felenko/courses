$ echo 219 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/target   # спускаємось
$ echo 232 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/fail     # ламаємо sched:active
$ echo 233 | sudo tee /sys/devices/system/cpu/cpu3/hotplug/target
tee: /sys/devices/system/cpu/cpu3/hotplug/target: Resource temporarily unavailable
$ cat /sys/devices/system/cpu/cpu3/hotplug/state
219
$ sudo dmesg | tail -3
cpucache: teardown cpu=3 злито 8, у пулі 16
cpucache: startup  cpu=3 count=8 (біжу на cpu3)
cpucache: teardown cpu=3 злито 8, у пулі 24
