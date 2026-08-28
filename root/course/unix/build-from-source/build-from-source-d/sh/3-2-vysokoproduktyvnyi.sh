# 1. Конфігурація середовища збірки
meson setup build \
    --buildtype=release \
    --prefix=/opt/mytool \
    -Dstrip=true

# 2. Компіляція через Ninja (автоматично використовує всі ядра CPU)
ninja -C build

# 3. Запуск автоматичних тестів проєкту
meson test -C build

# 4. Встановлення артефактів
meson install -C build
