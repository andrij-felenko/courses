# Налаштування конфігурації у двох різних каталогах
cmake -B build_alpha -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake -B build_beta_path -G Ninja -DCMAKE_BUILD_TYPE=Release

# Компіляція артефактів
cmake --build build_alpha
cmake --build build_beta_path

# Порівняння результатів
sha256sum build_alpha/app build_beta_path/app
