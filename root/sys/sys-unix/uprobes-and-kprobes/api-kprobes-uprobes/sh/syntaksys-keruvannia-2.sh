# 1. Знайти зміщення функції malloc у бібліотеці libc
OFFSET=$(nm -D /lib/x86_64-linux-gnu/libc.so.6 | grep 'W malloc$' | awk '{print "0x"$1}')

# 2. Зареєструвати uprobe на функцію malloc
echo "p:libc_malloc /lib/x86_64-linux-gnu/libc.so.6:$OFFSET size=%di:u64" >> /sys/kernel/tracing/uprobe_events

# 3. Зареєструвати uretprobe на повернення з malloc (отримання вказівника на пам'ять)
echo "r:libc_malloc_ret /lib/x86_64-linux-gnu/libc.so.6:$OFFSET ptr=\$retval:u64" >> /sys/kernel/tracing/uprobe_events

# 4. Увімкнути зонди
echo 1 > /sys/kernel/tracing/events/uprobes/libc_malloc/enable
