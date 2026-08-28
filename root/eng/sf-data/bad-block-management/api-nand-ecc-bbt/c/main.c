#include <stdint.h>

#define NAND_MAX_CHIPS        8
#define NAND_BBT_USE_FLASH    0x00020000
#define NAND_BBT_NO_OOB       0x00040000
#define NAND_BBT_SCANALLPAGES 0x00000400
#define NAND_BBT_VERSION      0x00000020
#define NAND_BBT_CREATE       0x00000001

struct nand_bbt_descr {
    int      options;                      // Бітові прапорці конфігурації
    int      pages[NAND_MAX_CHIPS];        // Номери сторінок, де збережено BBT
    int      offs;                         // Зміщення сигнатури або даних у сторінці
    int      veroffs;                      // Зміщення байта версії
    uint8_t  version[NAND_MAX_CHIPS];      // Поточна версія таблиці
    int      len;                          // Довжина сигнатури
    int      maxblocks;                    // Кількість блоків від кінця кристала
    char     *pattern;                     // Магічний патерн ("Bbt0" / "1tbB")
};
