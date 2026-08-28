# 1. джерела — без --recursive, підмодулів немає
git clone -j8 https://github.com/mavlink/qgroundcontrol.git
cd qgroundcontrol

# 2. системні залежності (на Linux потрібні права root)
python3 tools/setup/install_dependencies --platform debian

# 3. Qt потрібної версії з потрібними модулями — окремо, інсталятором Qt

# 4. конфігурація: перевірка машини, добування, підготовка генераторів
~/Qt/6.11.1/gcc_64/bin/qt-cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug

# 5. збірка: кодогенерація, компіляція, лінкування
cmake --build build

# 6. запуск
./build/QGroundControl
