# 1. Увімкнення графіку викликів функцій для підсистеми configfs.
#    Шаблон беремо в лапки, інакше оболонка спробує розкрити його
#    як маску імен файлів у поточному каталозі.
echo function_graph > /sys/kernel/tracing/current_tracer
echo 'configfs_*' > /sys/kernel/tracing/set_ftrace_filter
echo 'vfs_mkdir'  >> /sys/kernel/tracing/set_ftrace_filter
echo 'vfs_rmdir'  >> /sys/kernel/tracing/set_ftrace_filter
echo 'demo_group_*' >> /sys/kernel/tracing/set_ftrace_filter

# 2. Очищення буфера трасування та запуск спостереження
echo > /sys/kernel/tracing/trace
echo 1 > /sys/kernel/tracing/tracing_on
mkdir /sys/kernel/config/demo_target/test_node
rmdir /sys/kernel/config/demo_target/test_node
echo 0 > /sys/kernel/tracing/tracing_on

# 3. Перегляд траси викликів у ядрі
cat /sys/kernel/tracing/trace | head -n 30
