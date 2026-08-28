# 1. Запис подій перемикання контексту та блокового вводу-виводу під час виконання команди 'ls -la'
sudo trace-cmd record -e sched:sched_switch -e block:block_rq_issue ls -la /

# 2. Збір траси за допомогою function_graph для конкретного PID протягом 5 секунд
sudo trace-cmd record -p function_graph -g sys_openat2 -P 1234 sleep 5

# 3. Декодування та відображення збереженого файлу trace.dat
trace-cmd report

# 4. Моніторинг подій у реальному часі без збереження у файл (аналог trace_pipe)
sudo trace-cmd stream -e syscalls:sys_enter_read
