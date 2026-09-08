# GDB Скрипт посмертного аналізу аварійного дампа мікроконтролера
# Запуск: arm-none-eabi-gdb firmware.elf -x analyze_core.gdb

set pagination off
set print pretty on

echo \n========================================\n
echo   ПОСМЕРТНИЙ АНАЛІЗ CORE DUMP (FreeRTOS)   \n
echo ========================================\n\n

# Завантаження символів налагодження DWARF
file firmware.elf

echo [1/4] Регістри аварійного контексту процесора:\n
info registers

echo \n[2/4] Зворотне трасування викликів (Backtrace):\n
backtrace full

echo \n[3/4] Вихідний код навколо місця збою:\n
list *$pc

echo \n[4/4] Локальні змінні активного стек-фрейму:\n
info locals
info args

echo \n========================================\n
echo   Аналіз завершено. Рядок збою знайдено.   \n
echo ========================================\n
quit
