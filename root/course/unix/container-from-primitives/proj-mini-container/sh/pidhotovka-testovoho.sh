# 1. Створення каталогу для кореня контейнера
mkdir -p /tmp/alpine-rootfs

# 2. Завантаження та розпакування мінімального образу Alpine
curl -sSL https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/x86_64/alpine-minirootfs-3.20.0-x86_64.tar.gz \
  | tar -xz -C /tmp/alpine-rootfs

# 3. Компіляція утиліти
gcc -O2 -Wall minibox.c -o minibox

# 4. Запуск ізольованої оболонки
sudo ./minibox /tmp/alpine-rootfs /bin/sh
