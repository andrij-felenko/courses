static FATFS fs;     // об'єкт тому — глобальний, живе весь час роботи
FIL file;            // об'єкт файлу
FRESULT fr;

fr = f_mount(&fs, "", 1);                 // примонтувати том; 1 = негайно
if (fr != FR_OK) {
    return fr;                            // немає файлової системи — далі немає сенсу
}

// FA_OPEN_APPEND: відкрити, а як нема — створити; писати в кінець
fr = f_open(&file, "log.csv", FA_WRITE | FA_OPEN_APPEND);
if (fr != FR_OK) {
    return fr;
}

UINT written;                            // скільки байтів справді записано
const char *line = "12.4,1013,OK\n";
fr = f_write(&file, line, strlen(line), &written);
if (fr != FR_OK || written != strlen(line)) {
    // записалося менше, ніж просили, — найімовірніше, носій заповнений
    f_close(&file);
    return fr;
}

f_close(&file);                          // ось тут дані стають надійними (див. далі)
