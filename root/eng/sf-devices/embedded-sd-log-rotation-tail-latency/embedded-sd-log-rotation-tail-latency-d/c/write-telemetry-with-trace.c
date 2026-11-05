#include "ff.h"
#include <stdio.h>

// Демонстрація прихованих викликів FatFs під час розширення файлу
FRESULT write_telemetry_with_trace(FIL *fp, const void *buff, UINT btw, UINT *bw) {
    FRESULT res;
    DWORD clst_before = fp->clust;
    
    // Запис даних через стандартний інтерфейс
    res = f_write(fp, buff, btw, bw);
    
    // Перевірка: чи відбулася зміна кластера під час цієї операції
    if (res == FR_OK && fp->clust != clst_before) {
        // У цей момент FatFs виконала:
        // 1. Пошук вільного кластера в таблиці FAT
        // 2. Модифікацію сектора FAT1 та FAT2
        // 3. Перезапис сектора директорії (Directory Entry)
        // Саме ці операції спричиняють апаратну хвостову затримку SD-карти!
        printf("Увага: відбулося розширення файлу! Новий кластер: %lu\n", (unsigned long)fp->clust);
    }
    
    return res;
}
