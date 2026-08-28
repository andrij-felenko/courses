# 1. переконатися, що таблиця змонтована
mountpoint -q /proc/sys/fs/binfmt_misc || \
    mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc

# 2. завести формат: файли з розширенням .txt віддавати переглядачеві
echo ':showtext:E::txt::/usr/bin/less:' > /proc/sys/fs/binfmt_misc/register

# 3. перевірити, що ядро розгорнуло саме те, що малося на увазі
cat /proc/sys/fs/binfmt_misc/showtext
#   enabled
#   interpreter /usr/bin/less
#   flags:
#   extension .txt

# 4. спробувати в ділі (у теці, змонтованій без noexec)
printf 'привіт\n' > ./nota.txt && chmod +x ./nota.txt && ./nota.txt

# 5. тимчасово вимкнути, не втрачаючи запису
echo 0 > /proc/sys/fs/binfmt_misc/showtext

# 6. прибрати остаточно — файл зникне разом із записом
echo -1 > /proc/sys/fs/binfmt_misc/showtext
