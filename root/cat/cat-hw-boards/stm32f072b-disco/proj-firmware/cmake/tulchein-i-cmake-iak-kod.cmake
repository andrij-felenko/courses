cmake_minimum_required(VERSION 3.20)
project(disco_fw C ASM)

set(CMAKE_C_STANDARD 11)

add_executable(disco_fw.elf
    startup_stm32f072.s        # старт-код (таблиця векторів + скидання)
    main.c)

# Скрипт лінкера розкладає код у Flash, а змінні — в SRAM цього чипа.
# Файл stm32f072rb.ld описує: Flash 128К @ 0x08000000, RAM 16К @ 0x20000000.
target_link_options(disco_fw.elf PRIVATE
    -T${CMAKE_SOURCE_DIR}/stm32f072rb.ld
    -mcpu=cortex-m0 -mthumb
    -nostartfiles                     # свій startup, стандартний не потрібен
    -Wl,--gc-sections                 # викинути невживаний код — критично при 128 КБ
    -Wl,-Map=disco_fw.map)            # карта пам'яті — видно, що скільки з'їло

target_compile_options(disco_fw.elf PRIVATE
    -mcpu=cortex-m0 -mthumb
    -Og -g3                           # -Og: оптимізація, дружня до дебагу
    -ffunction-sections -fdata-sections
    -Wall -Wextra)

# Після збірки: зробити .bin і показати, скільки Flash/RAM зайнято.
add_custom_command(TARGET disco_fw.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O binary disco_fw.elf disco_fw.bin
    COMMAND ${CMAKE_SIZE} disco_fw.elf)

# Зручна ціль `make flash`: залити прошивку через ST-LINK за OpenOCD.
add_custom_target(flash
    COMMAND openocd -f interface/stlink.cfg -f target/stm32f0x.cfg
            -c "program disco_fw.elf verify reset exit"
    DEPENDS disco_fw.elf)
