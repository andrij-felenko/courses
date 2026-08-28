# Синхронізація файлової системи плати з локальним каталогом sysroot
mkdir -p /opt/sysroots/target-board
rsync -avz --delete \
    --exclude='/proc/*' \
    --exclude='/sys/*' \
    --exclude='/dev/*' \
    --exclude='/run/*' \
    --exclude='/tmp/*' \
    --exclude='/mnt/*' \
    --exclude='/media/*' \
    --exclude='/home/*' \
    root@192.168.1.100:/ /opt/sysroots/target-board/
