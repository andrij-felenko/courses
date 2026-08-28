# Пристрій перезавантажився, підключаємо USB, читаємо дамп із Flash
$ idf.py coredump-info
Loading core dump from device...

==================== CURRENT THREAD REGISTERS =====================
pc       0x400d1f88   sensor_read + 12
exccause 0x1d         (StoreProhibitedCause)
excvaddr 0x00000000
a1 (sp)  0x3ffb6e80

==================== BACKTRACE ====================================
#0  sensor_read (dev=0x3ffb1234, buf=0x0) at main/sensor.c:88
#1  0x400d2abc in update_sensors () at main/tasks.c:45
#2  0x400d2f10 in sensor_task (arg=0x0) at main/tasks.c:120

==================== ALL THREADS =================================
'sensor_task'  → sensor_read, sensor.c:88   (crashed)
'wifi_task'    → xQueueReceive, queue.c:112  (blocked on queue)
'app_task'     → xSemaphoreTake, semphr.h    (blocked on semaphore)
