# === Термінал 1: OpenOCD ===
$ idf.py openocd
Open On-Chip Debugger v0.12.0
Info : esp32: Target halted, PC=0x400D1ABC
Info : Listening on port 3333 for gdb connections

# === Термінал 2: GDB ===
$ idf.py gdb
(gdb) target remote :3333
Remote debugging using :3333
0x400D1ABC in esp_restart ()

(gdb) break app_main
Breakpoint 1 at 0x400D2010: file main/main.c, line 42.

(gdb) c
Continuing.
Breakpoint 1, app_main () at main/main.c:42
42          config_t cfg = { .rate = DEFAULT_RATE };

(gdb) p cfg.rate
$1 = 100

(gdb) bt
#0  app_main () at main/main.c:42
#1  0x400D0888 in main_task (args=0x0) at /idf/components/freertos/app_startup.c:208
