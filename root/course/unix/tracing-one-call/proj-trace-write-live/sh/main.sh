# Переходимо в каталог керування трасуванням
cd /sys/kernel/tracing

# 1. Тимчасово вимикаємо запис для безпечної конфігурації
echo 0 > tracing_on
echo nop > current_tracer
echo > trace

# 2. Встановлюємо плагін графа функцій
echo function_graph > current_tracer

# 3. Вказуємо кореневу функцію, від якої будувати дерево викликів
echo ksys_write > set_graph_function

# 4. Обмежуємо глибину дерева (щоб зосередитися на ключових підсистемах)
echo 6 > max_graph_depth

# 5. Вказуємо PID нашої запущеної програми (наприклад, 4128)
echo 4128 > set_ftrace_pid

# 6. Вмикаємо запис траси
echo 1 > tracing_on
