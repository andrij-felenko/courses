# 1. Перехід у каталог трасувальника ftrace
cd /sys/kernel/tracing

# 2. Активація подій трасування підсистеми PM QoS
echo 1 > events/power/pm_qos_add_request/enable
echo 1 > events/power/pm_qos_update_request/enable
echo 1 > events/power/pm_qos_remove_request/enable

# 3. Перегляд потокового виводу подій трасування
cat trace_pipe
