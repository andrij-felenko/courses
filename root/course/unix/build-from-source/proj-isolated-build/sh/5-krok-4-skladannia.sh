cd /tmp/build-workspace/sources

# Спрямовуємо pkg-config на метадані у проміжному каталозі
export PKG_CONFIG_PATH="/tmp/build-workspace/stage/opt/netbridge/lib/pkgconfig"

# Перевірка: чи знаходить pkg-config нашу версію libuv
pkg-config --modversion libuv
# Повинно вивести: 1.48.0

# Компіляція та лінкування з прапорцем RUNPATH
gcc -O3 -Wall \
    $(pkg-config --cflags libuv) \
    netbridge.c \
    $(pkg-config --libs libuv) \
    -Wl,-rpath,'$ORIGIN/../lib' \
    -Wl,--enable-new-dtags \
    -o netbridge

# Перевірка заголовків скомпільованого ELF бінарника
readelf -d netbridge | grep -E '(RUNPATH|NEEDED)'
