# Приклад використання реєстру defer:
TEMP_DIR=$(mktemp -d)
defer "rm -rf '${TEMP_DIR}'"

exec 200>/var/lock/app.lock
flock -n 200
defer "exec 200>&-"

mount /dev/nvme0n1p1 /mnt/stage
defer "umount -l /mnt/stage"
