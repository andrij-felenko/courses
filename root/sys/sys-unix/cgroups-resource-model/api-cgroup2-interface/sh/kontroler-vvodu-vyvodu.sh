lsblk -o NAME,MAJ:MIN                 # nvme0n1 259:0

# сто мегабайтів на читання, п'ятдесят на запис
echo "259:0 rbps=104857600 wbps=52428800" > /sys/fs/cgroup/build/io.max

# зняти стелю: у ключованому файлі пишемо лише те, що міняємо
echo "259:0 rbps=max wbps=max" > /sys/fs/cgroup/build/io.max

# вимога з іншого боку: база даних не мусить чекати довше за 2 мс
echo "259:0 target=2000" > /sys/fs/cgroup/db/io.latency
