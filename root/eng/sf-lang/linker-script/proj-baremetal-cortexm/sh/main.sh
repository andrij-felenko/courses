# Компіляція сирцевих файлів у позиційно-незалежні об'єктні файли
arm-none-eabi-gcc -c -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 \
    -O2 -ffunction-sections -fdata-sections -Wall startup.c -o startup.o

arm-none-eabi-gcc -c -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 \
    -O2 -ffunction-sections -fdata-sections -Wall main.c -o main.o

# Компонування з використанням stm32f4.ld та генерацією firmware.map
arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 \
    -Tstm32f4.ld -Wl,-Map=firmware.map,--cref,--gc-sections \
    -nostartfiles -o firmware.elf startup.o main.o
