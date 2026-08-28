# 1. Генерація конфігурації
./autogen.sh
./configure \
    --prefix=/opt/netbridge \
    --enable-shared \
    --disable-static \
    CFLAGS="-O3 -march=native -fPIC"

# 2. Паралельна компіляція з використанням усіх ядер процесора
make -j$(nproc)

# 3. Інсталяція у проміжний каталог stage замість кореня системи
make install DESTDIR=/tmp/build-workspace/stage
