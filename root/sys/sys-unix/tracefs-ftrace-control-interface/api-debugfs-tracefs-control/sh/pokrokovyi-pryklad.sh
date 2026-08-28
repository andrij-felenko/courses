# 1. Переконатися, що символ узагалі є в цьому ядрі (інакше запис поверне EINVAL)
$ sudo grep ' do_sys_open$' /proc/kallsyms

# 2. Створення kprobe на функцію do_sys_open із витягуванням першого аргументу (dfd)
#    %di — регістр першого аргументу x86_64; форма +0(%di) розіменувала б його як вказівник
$ echo 'p:my_open_probe do_sys_open dfd=%di:s32' | sudo tee /sys/kernel/tracing/kprobe_events

# 3. Перевірка створення події в ієрархії events
$ ls -l /sys/kernel/tracing/events/kprobes/my_open_probe/

# 4. Увімкнення створеного динамічного зонду
$ echo 1 | sudo tee /sys/kernel/tracing/events/kprobes/my_open_probe/enable

# 5. Перегляд згенерованих подій
$ sudo cat /sys/kernel/tracing/trace_pipe

# 6. Вимкнення та вилучення створеного зонду
$ echo 0 | sudo tee /sys/kernel/tracing/events/kprobes/my_open_probe/enable
$ echo '-:kprobes/my_open_probe' | sudo tee /sys/kernel/tracing/kprobe_events
