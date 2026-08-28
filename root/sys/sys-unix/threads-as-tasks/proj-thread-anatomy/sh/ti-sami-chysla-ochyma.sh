$ ls /proc/1200/task
1200  1203  1204  1205

$ grep -H '' /proc/1200/task/*/comm
/proc/1200/task/1200/comm:leader
/proc/1200/task/1203/comm:worker-1
/proc/1200/task/1204/comm:worker-2
/proc/1200/task/1205/comm:worker-3

$ grep -E '^(Tgid|Pid|Threads|SigBlk):' /proc/1200/task/1203/status
Tgid:    1200
Pid:     1203
Threads: 4
SigBlk:  0000000000000000

$ grep -E '^(Tgid|Pid|SigBlk):' /proc/1200/task/1200/status
Tgid:    1200
Pid:     1200
SigBlk:  0000000000000200
