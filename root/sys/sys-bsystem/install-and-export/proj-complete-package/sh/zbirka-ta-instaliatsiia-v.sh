# 1. Конфігурація проєкту в режимі Release із зазначенням префікса інсталяції
cmake -B build -S . \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/tmp/hyperion-dist

# 2. Компіляція двійкових артефактів
cmake --build build --config Release

# 3. Виконання інсталяції артефактів у заданий префікс
cmake --install build
