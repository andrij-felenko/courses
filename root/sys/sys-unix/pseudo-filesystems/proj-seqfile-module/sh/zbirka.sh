$ make
$ sudo insmod heartbeat.ko
$ ls -l /proc/heartbeat
-r--r--r-- 1 root root 0 сер  7 12:31 /proc/heartbeat
$ cat /proc/heartbeat
uptime_ms   1842517
reader_pid  9317
reader_comm cat
shows       1
$ cat /proc/heartbeat
uptime_ms   1846093
reader_pid  9319
reader_comm cat
shows       2
