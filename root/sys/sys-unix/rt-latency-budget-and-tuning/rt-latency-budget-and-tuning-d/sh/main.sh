# Налаштування трасувальника ftrace для пошуку затримок RT
echo wakeup_rt > /sys/kernel/tracing/current_tracer
echo 0 > /sys/kernel/tracing/tracing_max_latency   # скинути попередній максимум
echo 1 > /sys/kernel/tracing/tracing_on

# Запуск навантаження (stress-ng) та вимірювача cyclictest
cyclictest -p 80 -m -n -i 1000 -l 100000

# Перегляд зафіксованого трасування з джерелом максимальної затримки
cat /sys/kernel/tracing/trace
