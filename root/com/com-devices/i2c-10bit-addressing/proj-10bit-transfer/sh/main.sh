# Перехід до віртуальної файлової системи трасування
cd /sys/kernel/tracing

# Очищення буфера трасування
echo 0 > tracing_on
echo > trace

# Увімкнення подій драйвера I2C
echo 1 > events/i2c/i2c_read/enable
echo 1 > events/i2c/i2c_write/enable
echo 1 > events/i2c/i2c_result/enable

# Запуск запису
echo 1 > tracing_on

# Виконання тестової 10-бітної транзакції через i2ctransfer
i2ctransfer -y 1 w1@0x248+ 0x10 r2@0x248+

# Зупинка трасування та перегляд журналу
echo 0 > tracing_on
cat trace
