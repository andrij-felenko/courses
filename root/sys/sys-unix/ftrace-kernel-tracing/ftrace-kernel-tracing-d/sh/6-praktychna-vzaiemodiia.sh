# 1. Перейти у каталог tracefs
cd /sys/kernel/tracing

# 2. Вимкнути запис на час налаштування
echo 0 > tracing_on

# 3. Обрати трасер функцій
echo function > current_tracer

# 4. Встановити фільтр лише на функції відкриття файлів
echo "do_sys_open*" > set_ftrace_filter

# 5. Увімкнути запис
echo 1 > tracing_on

# 6. Переглянути результати трасування
cat trace_pipe
