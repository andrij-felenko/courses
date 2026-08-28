# 1. Зупиняємо поточне трасування та очищаємо буфер
echo 0 > /sys/kernel/tracing/tracing_on
echo > /sys/kernel/tracing/trace

# 2. Встановлюємо маску відстеження лише для CPU 1 (бітова маска: 2^1 = 2)
echo 2 > /sys/kernel/tracing/tracing_cpumask

# 3. Активуємо ключові точкові події
echo 1 > /sys/kernel/tracing/events/irq_vectors/local_timer_entry/enable
echo 1 > /sys/kernel/tracing/events/sched/sched_switch/enable
echo 1 > /sys/kernel/tracing/events/raw_syscalls/sys_enter/enable
echo 1 > /sys/kernel/tracing/events/workqueue/workqueue_execute_start/enable

# 4. Вмикаємо кільцевий буфер трасування
echo 1 > /sys/kernel/tracing/tracing_on

# 5. Виконуємо досліджуваний низькозатримковий додаток на CPU 1
taskset -c 1 ./low_latency_app

# 6. Зупиняємо трасування
echo 0 > /sys/kernel/tracing/tracing_on

# 7. Переглядаємо перші 40 подій трасування
cat /sys/kernel/tracing/trace | head -n 40
