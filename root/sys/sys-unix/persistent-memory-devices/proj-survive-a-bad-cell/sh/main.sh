$ sudo ndctl inject-error --block=20480 --count=1 namespace0.0
$ sudo ndctl start-scrub && sudo ndctl wait-scrub
$ cat /sys/block/pmem0/badblocks
16384 1

$ sudo ./pmsafe /mnt/pmem/data.bin
збій: адреса 0x7f3a12c04000, зсув у файлі 4194304, ділянка 4096 Б, BUS_MCEERR_AR (спожито)
  сектор пристрою 16384 — у списку badblocks
  запис списку: 16384 1
прочитано без збоїв 268431360 Б
розчищено ділянок   1 (втрачено 4096 Б — брати з копії)

$ cat /sys/block/pmem0/badblocks
$
