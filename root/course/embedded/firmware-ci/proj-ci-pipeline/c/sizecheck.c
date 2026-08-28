// tools/sizecheck.c — воротар розміру: читає text/data/bss і падає,
// якщо Flash (.text+.data) чи RAM (.data+.bss) перевищив бюджет.
//
// Виклик:  arm-none-eabi-size firmware.elf | ./sizecheck <flash_КБ> <ram_КБ>
// Код виходу: 0 — влізло, 1 — пробито бюджет, 2 — не розібрали вхід.

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: size ... | %s <flash_kb> <ram_kb>\n", argv[0]);
        return 2;
    }

    // Бюджети з аргументів (у КБ) — переводимо в байти.
    long flash_budget = strtol(argv[1], NULL, 10) * 1024L;
    long ram_budget   = strtol(argv[2], NULL, 10) * 1024L;

    // Вивід `size` у форматі Berkeley: перший рядок — заголовок, другий — числа.
    char line[256];
    if (!fgets(line, sizeof line, stdin)) return 2;   // проковтнути заголовок
    long text = 0, data = 0, bss = 0;
    if (fgets(line, sizeof line, stdin) == NULL ||
        sscanf(line, "%ld %ld %ld", &text, &data, &bss) != 3) {
        fprintf(stderr, "sizecheck: не розібрав вивід size\n");
        return 2;
    }

    long flash_used = text + data;   // код + початкові значення
    long ram_used   = data + bss;    // усі змінні під час роботи

    printf("Flash: %ld / %ld байт (%.1f%%)\n",
           flash_used, flash_budget, 100.0 * flash_used / flash_budget);
    printf("RAM:   %ld / %ld байт (%.1f%%)\n",
           ram_used,   ram_budget,   100.0 * ram_used   / ram_budget);

    int fail = 0;
    if (flash_used > flash_budget) {
        fprintf(stderr, "FAIL: Flash пробито на %ld байт\n",
                flash_used - flash_budget);
        fail = 1;
    }
    if (ram_used > ram_budget) {
        fprintf(stderr, "FAIL: RAM пробито на %ld байт\n",
                ram_used - ram_budget);
        fail = 1;
    }
    return fail;   // 1 → крок червоний → ворота замкнено
}
