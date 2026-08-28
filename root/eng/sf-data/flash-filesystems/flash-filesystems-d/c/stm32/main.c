// STM32Cube: FatFs як middleware над SD-карткою (у CubeMX увімкнено FATFS + SDMMC/SPI).
#include "fatfs.h"

static FATFS fs;                     // об'єкт тому
static FIL   file;
static char  line[64];

void log_demo(void) {
  // Змонтувати том за замовчуванням; 1 — монтувати негайно, а не при першому доступі.
  if (f_mount(&fs, "", 1) != FR_OK) { Error_Handler(); }

  // FA_OPEN_APPEND — відкрити (створивши за потреби) з позицією В КІНЦІ файлу:
  // старі рядки лишаються недоторкані (на відміну від FA_CREATE_ALWAYS, що затирає).
  if (f_open(&file, "log.txt", FA_WRITE | FA_OPEN_APPEND) != FR_OK) { return; }
  f_puts("08:01  старт\n", &file);
  f_puts("08:05  кнопка\n", &file);
  f_close(&file);                    // тільки після f_close() дані напевно на носії

  // Прочитати весь файл від початку до кінця.
  if (f_open(&file, "log.txt", FA_READ) == FR_OK) {
    while (f_gets(line, sizeof(line), &file) != NULL) printf("%s", line);
    f_close(&file);
  }
  f_mount(NULL, "", 0);              // розмонтувати
}
