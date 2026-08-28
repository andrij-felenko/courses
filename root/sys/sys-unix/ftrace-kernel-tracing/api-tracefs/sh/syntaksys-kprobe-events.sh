# 1. Трасувати вхід у функцію do_sys_openat2, витягуючи аргумент dfd з регістру %di та шлях до файлу з %si
echo 'p:my_open do_sys_openat2 dfd=%di filename=+0(%si):string' >> /sys/kernel/tracing/kprobe_events

# 2. Трасувати значення, що повертає функція do_sys_openat2 (регістр %ax)
echo 'r:my_open_ret do_sys_openat2 ret=$retval' >> /sys/kernel/tracing/kprobe_events

# 3. Активація створеної динамічної події
echo 1 > /sys/kernel/tracing/events/kprobes/my_open/enable

# 4. Видалення динамічної точки трасування
echo 0 > /sys/kernel/tracing/events/kprobes/my_open/enable
echo '-:kprobes/my_open' >> /sys/kernel/tracing/kprobe_events
