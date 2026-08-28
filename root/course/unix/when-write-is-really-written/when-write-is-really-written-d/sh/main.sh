# Перевірка режиму кешу запису блокового пристрою
cat /sys/block/nvme0n1/queue/write_cache
# Вивід: "write back" (є летючий кеш) або "write through" (кеш вимкнено/наскрізний)

# Перевірка апаратної підтримки FUA (Force Unit Access)
cat /sys/block/nvme0n1/queue/fua
# Вивід: 1 (підтримується апаратно) або 0 (емулюється через FLUSH)

# Перевірка стану летючого кешу NVMe через nvme-cli (Feature 0x06)
sudo nvme get-feature /dev/nvme0 -f 0x06
# get-feature:0x06 (Volatile Write Cache), Current value:0x00000001 (кеш увімкнено)

# Перевірка кешу SATA дисків через smartctl
sudo smartctl -g wcache /dev/sda
