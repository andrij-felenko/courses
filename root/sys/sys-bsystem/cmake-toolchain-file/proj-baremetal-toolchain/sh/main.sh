# 1. Генерація системи збірки із зазначенням файлу тулчейна
cmake -B build -S . --toolchain cmake/arm-none-eabi.cmake -G Ninja

# 2. Компіляція бінарних файлів та генерація образів .hex/.bin
cmake --build build

# 3. Перевірка розміру секцій скомпільованого двійкового файлу
# arm-none-eabi-size build/firmware.elf
# text    data     bss     dec     hex filename
#  584       0       0     584     248 firmware.elf
