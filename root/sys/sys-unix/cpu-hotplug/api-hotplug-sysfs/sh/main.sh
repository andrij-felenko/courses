# 1. знайти свій стан за НАЗВОЮ
grep percpu_cnt /sys/devices/system/cpu/hotplug/states
# 140: lib/percpu_cnt:online

# 2. опустити ядро процесора рівно до нього й підняти назад
echo 140 > /sys/devices/system/cpu/cpu4/hotplug/target
cat /sys/devices/system/cpu/cpu4/hotplug/state     # 140
echo 169 > /sys/devices/system/cpu/cpu4/hotplug/target

# 3. зламати перехід саме в цій точці
echo 140 > /sys/devices/system/cpu/cpu4/hotplug/fail
echo 0 > /sys/devices/system/cpu/cpu4/online
# -bash: echo: write error: Resource temporarily unavailable
cat /sys/devices/system/cpu/cpu4/hotplug/fail      # -1: спрацювало й скинулося
