$ sudo ./proc_spy_cpp 8920
====================================================
ДІАГНОСТИЧНИЙ ПАСПОРТ ПРОЦЕСУ PID: 8920
====================================================
Стан (State):             D (disk sleep)
Кількість ниток (Threads):16
Резидентна пам'ять (RSS): 8941200 KiB (8731.64 MiB)
Добровільні перемикання:  452019
Примусові перемикання:    3100
Частка добровільних:      99.3%

=== Канал очікування ядра (wchan) ===
blk_mq_make_request

=== Стек викликів ядра сплячого потоку (stack) ===
[<0>] io_schedule+0x42/0x70
[<0>] blk_mq_make_request+0x1a2/0x320
[<0>] generic_make_request+0xcf/0x180
[<0>] submit_bio+0x68/0x140
[<0>] ext4_writepages+0x590/0xa80
[<0>] do_writepages+0x41/0xd0
[<0>] __filemap_fdatawrite_range+0xd5/0x110
[<0>] file_write_and_wait_range+0x44/0x90
[<0>] ext4_sync_file+0xeb/0x360
[<0>] vfs_fsync_range+0x49/0x80
[<0>] do_fsync+0x38/0x70
[<0>] __x64_sys_fsync+0x14/0x20
[<0>] do_syscall_64+0x5c/0x90
