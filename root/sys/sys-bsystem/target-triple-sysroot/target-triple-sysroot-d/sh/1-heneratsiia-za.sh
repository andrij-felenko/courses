# 1. Завантаження базових deb-пакетів для AArch64 (перша стадія)
sudo debootstrap --arch=arm64 --foreign bookworm /opt/sysroots/debian-arm64 http://deb.debian.org/debian

# 2. Копіювання статичного емулятора QEMU user mode всередину sysroot
sudo cp /usr/bin/qemu-aarch64-static /opt/sysroots/debian-arm64/usr/bin/

# 3. Виконання другої стадії розгортання всередині емульованого chroot
sudo chroot /opt/sysroots/debian-arm64 /debootstrap/debootstrap --second-stage

# 4. Установка необхідних -dev пакетів заголовків та бібліотек
sudo chroot /opt/sysroots/debian-arm64 apt-get update
sudo chroot /opt/sysroots/debian-arm64 apt-get install -y \
    build-essential libssl-dev zlib1g-dev libsqlite3-dev

# 5. Видалення емулятора після завершення підготовки
sudo rm /opt/sysroots/debian-arm64/usr/bin/qemu-aarch64-static
