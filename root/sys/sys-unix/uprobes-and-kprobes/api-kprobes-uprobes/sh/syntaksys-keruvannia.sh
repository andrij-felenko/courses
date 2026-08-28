# 1. Встановити kprobe на вхід у функцію sys_openat2 та витягнути ім'я файлу (RSI)
echo 'p:my_open do_sys_openat2 filename=+0(%si):string' >> /sys/kernel/tracing/kprobe_events

# 2. Встановити kretprobe на вихід з sys_openat2 та зчитати результат повернення ($retval / RAX)
echo 'r:my_open_ret do_sys_openat2 ret=$retval:s32' >> /sys/kernel/tracing/kprobe_events

# 3. Активувати створений зонд
echo 1 > /sys/kernel/tracing/events/kprobes/my_open/enable

# 4. Читати потік подій трасування
cat /sys/kernel/tracing/trace_pipe

# 5. Деактивувати та видалити зонд
echo 0 > /sys/kernel/tracing/events/kprobes/my_open/enable
echo '-:kprobes/my_open' >> /sys/kernel/tracing/kprobe_events
