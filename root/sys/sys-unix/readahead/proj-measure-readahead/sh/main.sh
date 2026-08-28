# 1. Файл, помітно більший за вільну пам'ять
free -m
dd if=/dev/urandom of=big.bin bs=1M count=8192
sync

# 2. Де він лежить і яка там стеля вікна
df --output=source big.bin
cat /sys/block/nvme0n1/queue/read_ahead_kb      # 128

# 3. Вісім прогонів: обхід × порада
cc -O2 -Wall -Wextra -o rabench rabench.c
for hint in none normal sequential random; do
    ./rabench big.bin seq  "$hint" 4096 0
    ./rabench big.bin rand "$hint" 4096 200000
done

# 4. Важча зброя, коли DONTNEED не бере (файл тримає ще хтось)
sudo sh -c 'sync; echo 1 > /proc/sys/vm/drop_caches'
