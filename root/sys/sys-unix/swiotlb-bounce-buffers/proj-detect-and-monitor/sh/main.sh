# 1. Скидання попередніх налаштувань трасувальника
echo 0 > /sys/kernel/tracing/tracing_on
echo > /sys/kernel/tracing/trace

# 2. Активація події swiotlb_bounced
echo 1 > /sys/kernel/tracing/events/swiotlb/swiotlb_bounced/enable

# 3. Запуск трасування на 5 секунд під час навантаження
echo 1 > /sys/kernel/tracing/tracing_on
sleep 5
echo 0 > /sys/kernel/tracing/tracing_on

# 4. Перегляд зібраних подій
head -n 20 /sys/kernel/tracing/trace
