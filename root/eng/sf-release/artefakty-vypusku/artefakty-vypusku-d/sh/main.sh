# 1. Створення ізольованого архіву символів DWARF
arm-none-eabi-objcopy --only-keep-debug firmware.elf firmware.debug

# 2. Очищення основного ELF-файлу від налагоджувальної інформації
arm-none-eabi-strip --strip-debug --strip-unneeded firmware.elf

# 3. Зв'язування очищеного бінарника з файлом символів через секцію .gnu_debuglink
arm-none-eabi-objcopy --add-gnu-debuglink=firmware.debug firmware.elf

# 4. Формування чистого лінійного бінарного образу для запису у Flash
arm-none-eabi-objcopy -O binary firmware.elf firmware.bin
