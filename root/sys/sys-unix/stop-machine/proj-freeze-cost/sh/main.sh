$ cd /sys/kernel/tracing          # старіші системи: /sys/kernel/debug/tracing
$ echo 0 > tracing_max_latency
$ echo irqsoff > current_tracer
$ echo 1 > tracing_on
$ sudo insmod freeze_cost.ko reps=1 && sudo rmmod freeze_cost
$ cat tracing_max_latency
41
$ head -6 trace
# irqsoff latency trace v1.1.5 on 6.8.0
# --------------------------------------------------------
# latency: 41 us, #4/4, CPU#3 | (M:desktop VP:0, KP:0, SP:0 HP:0 #P:8)
#    -----------------
#    | task: migration/3-27 (uid:0 nice:0 policy:1 rt_prio:99)
#    -----------------
