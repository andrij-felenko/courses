# Монтування віртуальної файлової системи debugfs (якщо не змонтована)
mount -t debugfs nodev /sys/kernel/debug

# Увімкнення трасування запитів та відповідей шини MMC/SDIO
echo 1 > /sys/kernel/debug/tracing/events/mmc/mmc_request_start/enable
echo 1 > /sys/kernel/debug/tracing/events/mmc/mmc_request_done/enable

# Очищення буфера та старт запису
echo > /sys/kernel/debug/tracing/trace
echo 1 > /sys/kernel/debug/tracing/tracing_on
