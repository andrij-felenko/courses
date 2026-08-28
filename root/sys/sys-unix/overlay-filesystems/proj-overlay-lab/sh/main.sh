# нижній шар — свій образ, змонтований лише для читання
truncate -s 1G /var/tmp/ovl-lower.img
mkfs.ext4 -q /var/tmp/ovl-lower.img
mkdir -p /mnt/lower
mount -o loop /var/tmp/ovl-lower.img /mnt/lower

# верхній шар, робочий каталог і точка збірки — другий образ
truncate -s 2G /var/tmp/ovl-upper.img
mkfs.ext4 -q /var/tmp/ovl-upper.img
mkdir -p /mnt/lab
mount -o loop /var/tmp/ovl-upper.img /mnt/lab
mkdir /mnt/lab/upper /mnt/lab/work /mnt/lab/merged
