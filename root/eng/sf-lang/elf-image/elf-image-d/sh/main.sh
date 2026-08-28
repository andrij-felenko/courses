# 1. Перегляд головного заголовка ELF (архітектура, точка входу, адреси таблиць)
arm-none-eabi-readelf -h firmware.elf

# 2. Перегляд таблиці завантажуваних сегментів (LMA, VMA, розміри filesz та memsz)
arm-none-eabi-readelf -l firmware.elf

# 3. Перегляд списку всіх секцій з їхніми прапорцями та адресами
arm-none-eabi-readelf -S firmware.elf

# 4. Пошук 20 найбільших символів у прошивці за розміром (деревний аналіз споживання пам'яті)
arm-none-eabi-nm --size-sort -C -r firmware.elf | head -n 20

# 5. Дизасемблювання секції коду зі співставленням сирцевих рядків C/C++
arm-none-eabi-objdump -d -S -C firmware.elf > firmware_disasm.txt

# 6. Перегляд налаштувань таблиць конструкторів .init_array
arm-none-eabi-readelf -x .init_array firmware.elf
