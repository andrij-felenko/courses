# === Термінал 1: сервер OpenOCD (зонд CMSIS-DAP + чип STM32F4) ===
$ openocd -f interface/cmsis-dap.cfg -f target/stm32f4x.cfg
Open On-Chip Debugger 0.12.0
Info : CMSIS-DAP: SWD supported
Info : SWD DPIDR 0x2ba01477
Info : stm32f4x.cpu: Cortex-M4 r0p1, halted
Info : Listening on port 3333 for gdb connections

# === Термінал 2: GDB чіпляється й піднімає сеанс ===
$ arm-none-eabi-gdb firmware.elf
(gdb) target remote :3333
Remote debugging using :3333
0x08000abc in Reset_Handler ()

(gdb) monitor reset halt          # команда йде в OpenOCD, не в GDB
target halted due to debug-request, current mode: Thread
xPSR: 0x01000000 pc: 0x08000abc

(gdb) load                        # залити свіжу прошивку з .elf у Flash
Loading section .text, size 0x4a80 lma 0x8000000
Loading section .data, size 0x110 lma 0x8004a80
Start address 0x08000abc, load size 19344

(gdb) break main
Breakpoint 1 at 0x8001200: file Src/main.c, line 88.

(gdb) c
Continuing.
Breakpoint 1, main () at Src/main.c:88
88          HAL_Init();

(gdb) bt
#0  main () at Src/main.c:88
