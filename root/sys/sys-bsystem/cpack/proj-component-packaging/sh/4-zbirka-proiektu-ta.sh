# Крок 1. Конфігурація та компіляція
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release
cmake --build build

# Крок 2. Генерація пакетів Debian (DEB)
cd build
cpack -G DEB

# Крок 3. Генерація пакетів Red Hat (RPM)
cpack -G RPM

# Крок 4. Генерація автономного архіву (TGZ)
cpack -G TGZ
