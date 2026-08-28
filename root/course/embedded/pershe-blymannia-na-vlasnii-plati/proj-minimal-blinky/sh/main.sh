# Компіляція версії на C
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -O1 -nostdlib -ffreestanding \
    -T link.ld startup.s main.c -o blinky.elf

# Компіляція версії на C++
arm-none-eabi-g++ -mcpu=cortex-m4 -mthumb -O1 -nostdlib -ffreestanding \
    -fno-exceptions -fno-rtti \
    -T link.ld startup.s main.cpp -o blinky.elf

# Отримання бінарного образу для прошивання
arm-none-eabi-objcopy -O binary blinky.elf blinky.bin
