// 1. Компіляція + лінкування КРОС-компілятором.
//    -mcpu каже, яке саме ядро цілі; --specs=nosys — без ОС (bare-metal).
//    Виконується на x86, але кожна інструкція на виході — це ARM Thumb.
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb \
    -T linker.ld --specs=nosys.specs \
    blink.c -o blink.elf

// 2. Витягуємо з ELF чистий образ для запису у Flash.
//    objcopy теж КРОС: розуміє ARM-секції, а сам біжить на x86.
arm-none-eabi-objcopy -O binary blink.elf blink.bin

// 3. Перевіряємо, ЩО саме ми зібрали — для ЯКОЇ архітектури.
arm-none-eabi-readelf -h blink.elf | grep Machine
//   → Machine: ARM        ← ось воно: бінарник для ARM,
//                            а зібрали ми його на x86, нічого не запускаючи
