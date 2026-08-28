# 1. Знаходження зміщення функції malloc у системній бібліотеці libc.
#    Значення залежить від конкретної збірки glibc — беріть своє, а не з прикладу
$ nm -D /lib/x86_64-linux-gnu/libc.so.6 | grep ' malloc$'
00000000000982d0 T malloc

# 2. Встановлення зонду на знайдене зміщення із витягуванням першого аргументу (%di)
$ echo 'p:user_malloc /lib/x86_64-linux-gnu/libc.so.6:0x982d0 bytes=%di:u64' | sudo tee /sys/kernel/tracing/uprobe_events

# 3. Увімкнення uprobe зонду
$ echo 1 | sudo tee /sys/kernel/tracing/events/uprobes/user_malloc/enable
