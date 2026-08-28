# 1. Конфігурація та генерація дерева збірки у теці build/
cmake -B build -S . \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/opt/mytool \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

# 2. Компіляція проєкту
cmake --build build -j $(nproc)

# 3. Інсталяція зібраних артефактів
cmake --install build
