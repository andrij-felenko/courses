# Покрокова перевірка стартового коду.
# Ужиток: arm-none-eabi-gdb firmware.elf -x tools/startup-check.gdb
# Перед цим в іншому терміналі: openocd -f interface/stlink.cfg -f target/stm32f4x.cfg

set confirm off
set pagination off
set print pretty on

# 1. Підключення до сервера налагодження OpenOCD
target extended-remote :3333

# 2. Апаратне скидання й зупинка ядра на першому такті
monitor reset halt

# 3. Точка зупину на точці входу
break Reset_Handler
continue

# 4. Стан ядра ДО першої інструкції стартового коду.
#    SP уже дорівнює _estack, PC — Reset_Handler: обидва значення ядро взяло
#    з перших двох слів векторної таблиці, ще нічого не виконавши.
info registers sp pc xpsr
printf "вершина стека з вектора: 0x%08X\n", *(unsigned int *)0x08000000
printf "точка входу з вектора:   0x%08X\n", *(unsigned int *)0x08000004
printf "Thumb-біт xPSR.T:        %d\n", ($xpsr >> 24) & 1

# 5. Кілька інструкцій копіювання .data — видно сам цикл, а не виклик memcpy
stepi 10
x/4xw &_sdata

# 6. Занулення .bss ще не відпрацювало: тут поки сміття після подачі живлення
x/16xb &_sbss

# 7. До входу в main() середовище має бути розгорнуте повністю
break main
continue

printf "\n--- стан на вході в main() ---\n"
printf ".data скопійовано:    %d\n", (g_boot_pattern == 0xA5A5A5A5)
printf ".init_array пройдено: %d\n", (g_ctor_witness == 0x00C0FFEE)
printf "CPACR (FPU):          0x%08X\n", *(unsigned int *)0xE000ED88
printf "VTOR:                 0x%08X\n", *(unsigned int *)0xE000ED08
printf "SHCSR:                0x%08X\n", *(unsigned int *)0xE000ED24

# 8. Скільки RAM з'їли глобальні змінні й скільки лишилося купі та стеку
printf "\n.data: %d байтів\n", (char *)&_edata - (char *)&_sdata
printf ".bss:  %d байтів\n", (char *)&_ebss - (char *)&_sbss
printf "вільно між _end і _estack: %d байтів\n", (char *)&_estack - (char *)&_end

# 9. Дві команди на випадок падіння.
#    `fault` друкує звіт, зібраний HardFault_Handler_C, разом із готовим
#    рядком для addr2line; `crash` навмисно спричиняє ділення на нуль,
#    щоб перевірити обробник на живому збої.
define fault
  print g_last_fault
  printf "\naddr2line: arm-none-eabi-addr2line -e firmware.elf 0x%08X\n", g_last_fault.frame.pc
end
document fault
Показати звіт про останній апаратний збій, зібраний HardFault_Handler_C.
end

define crash
  set var g_trigger_fault = 1
  continue
end
document crash
Спричинити ділення на нуль у main() і зупинитися в обробнику збою.
end

printf "\nдалі: `continue`, потім `crash` і `fault`\n"
