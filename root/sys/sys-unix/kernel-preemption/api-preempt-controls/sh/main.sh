# 1. чинна модель — якщо ядро динамічне
cat /sys/kernel/debug/sched/preempt

# 2. з чим складено — з ядра, якщо ввімкнено CONFIG_IKCONFIG_PROC
zcat /proc/config.gz | grep -E '^CONFIG_(PREEMPT|DEBUG_PREEMPT|DEBUG_ATOMIC_SLEEP)'

# 3. те саме з файлу дистрибутива, якщо /proc/config.gz немає
grep -E '^CONFIG_PREEMPT' /boot/config-$(uname -r)

# 4. чи потокові обробники переривань узагалі є
ps -eo pid,cls,rtprio,comm | grep -c 'irq/'
