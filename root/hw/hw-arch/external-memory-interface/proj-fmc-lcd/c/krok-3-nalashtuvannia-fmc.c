#include "stm32f4xx.h"      // CMSIS: FMC_Bank1, RCC, GPIO, біти з _Pos-суфіксами
#include <stdint.h>

// Дві «двері» до дисплея. D/C з'єднаний з лінією A18, шина 16-бітна,
// тому різниця адрес = 2^18 * 2 = 0x00080000 (див. розрахунок вище).
#define LCD_BASE   0x60000000u
#define LCD_CMD   (*(volatile uint16_t *)(LCD_BASE + 0x00000000u))  // A18 = 0 → команда
#define LCD_DATA  (*(volatile uint16_t *)(LCD_BASE + 0x00080000u))  // A18 = 1 → дані

void fmc_lcd_init(void) {
    // 1. Тактування: сам блок FMC і всі порти GPIO, куди виведені його ніжки.
    RCC->AHB3ENR |= RCC_AHB3ENR_FMCEN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIODEN | RCC_AHB1ENR_GPIOEEN
                  | RCC_AHB1ENR_GPIOFEN | RCC_AHB1ENR_GPIOGEN;
    // (Конкретні ніжки D0..D15, A18, ~NE1, ~NWE, ~NOE переводять у режим
    //  альтернативної функції AF12 — це рутина, тут її опускаємо задля ясності.)

    // 2. Керування банком 1 (регістр BCR1 = BTCR[0]).
    //    MTYP=SRAM(00), MWID=16 біт(01), WREN=1, MBKEN=1; EXTMOD=0 (спільні
    //    таймінги на читання й запис — режим A нам достатній).
    FMC_Bank1->BTCR[0] =
          (0u << FMC_BCR1_MTYP_Pos)     // тип пам'яті: SRAM
        | (1u << FMC_BCR1_MWID_Pos)     // ширина шини: 16 біт
        | FMC_BCR1_WREN                 // дозвіл запису
        | FMC_BCR1_MBKEN;               // увімкнути банк

    // 3. Таймінги банку 1 (регістр BTR1 = BTCR[1]) — числа з розрахунку.
    //    ADDSET=8 (біти 0..3), ADDHLD=0 (4..7), DATAST=3 (8..15), решта 0.
    FMC_Bank1->BTCR[1] =
          (8u << FMC_BTR1_ADDSET_Pos)   // ADDSET = 8 тактів
        | (0u << FMC_BTR1_ADDHLD_Pos)   // ADDHLD = 0 (не мультиплексуємо)
        | (3u << FMC_BTR1_DATAST_Pos);  // DATAST = 3 такти
}
