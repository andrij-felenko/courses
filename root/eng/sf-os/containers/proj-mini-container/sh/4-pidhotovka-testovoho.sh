# 1. Створення каталогу для rootfs
mkdir -p /tmp/alpine-rootfs

# 2. Експорт розпакованого образу Alpine Linux із Docker Hub
docker export $(docker create alpine:latest) | tar -C /tmp/alpine-rootfs -xf -

# 3. Компіляція програми на C
gcc -O2 -Wall minicontainer.c -o minicontainer

# 4. Компіляція програми на C++20
g++ -O2 -Wall -std=c++20 minicontainer.cpp -o minicontainer-cpp

# 5. Запуск ізольованої оболонки під керуванням нашого рантайму
sudo ./minicontainer /tmp/alpine-rootfs /bin/sh
