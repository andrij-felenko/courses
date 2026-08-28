#include "stm32f0xx.h"
#include <stdint.h>

// ── Адреси регістрів L3GD20 (з даташита) ──
#define L3GD20_WHO_AM_I    0x0F   // має повернути 0xD4 — «я справді L3GD20»
#define L3GD20_CTRL_REG1   0x20   // живлення + вмикання осей
#define L3GD20_CTRL_REG4   0x23   // діапазон (±250/500/2000 °/с)
#define L3GD20_OUT_X_L     0x28   // перший із шести байтів даних XYZ

#define SPI_READ   0x80           // біт 7: 1 = читання
#define SPI_AUTOINC 0x40          // біт 6: 1 = адреса росте сама

// ── CS на PC0: ручний вибір давача ──
static inline void cs_low(void)  { GPIOC->BSRR = (1u << (0 + 16)); } // скинути PC0 в 0
static inline void cs_high(void) { GPIOC->BSRR = (1u <<  0);       } // підняти PC0 в 1

// Обмін одним байтом: віддати tx, одночасно прийняти те, що виставив давач.
static uint8_t spi_xfer(uint8_t tx) {
    while (!(SPI2->SR & SPI_SR_TXE)) { }        // чекаємо, поки буфер передачі вільний
    *(volatile uint8_t *)&SPI2->DR = tx;        // 8-бітний запис у DR — важливо саме байтом
    while (!(SPI2->SR & SPI_SR_RXNE)) { }       // чекаємо, поки прийшов байт-відповідь
    return *(volatile uint8_t *)&SPI2->DR;
}

static void l3gd20_init(void) {
    // Тактування: порт B (лінії SPI), порт C (CS), сам блок SPI2.
    RCC->AHBENR  |= RCC_AHBENR_GPIOBEN | RCC_AHBENR_GPIOCEN;
    RCC->APB1ENR |= RCC_APB1ENR_SPI2EN;         // SPI2 сидить на шині APB1

    // PB13/14/15 → альтернативна функція AF0 (це і є SPI2 на цих виводах).
    for (int p = 13; p <= 15; p++) {
        GPIOB->MODER &= ~(3u << (p * 2));
        GPIOB->MODER |=  (2u << (p * 2));       // 10 = альтернативна функція
    }
    // AF0 для виводів 13..15 у старшому регістрі AFR[1] — нулі, тож явно чистимо.
    GPIOB->AFR[1] &= ~((0xFu << ((13 - 8) * 4)) |
                       (0xFu << ((14 - 8) * 4)) |
                       (0xFu << ((15 - 8) * 4)));

    // PC0 → звичайний вихід (CS), і одразу в 1 (давач не вибрано).
    GPIOC->MODER &= ~(3u << (0 * 2));
    GPIOC->MODER |=  (1u << (0 * 2));
    cs_high();

    // Налаштувати SPI2 як майстер, режим 3 (CPOL=1, CPHA=1 — так вимагає даташит L3GD20).
    // Дільник такту: 48 МГц / 32 = 1.5 МГц — з запасом у межах 10 МГц, що тримає L3GD20.
    SPI2->CR1 = SPI_CR1_MSTR                     // майстер
              | SPI_CR1_CPOL | SPI_CR1_CPHA      // режим 3
              | (3u << SPI_CR1_BR_Pos)           // BR = 011 → поділ на 32
              | SPI_CR1_SSM | SPI_CR1_SSI;       // CS керуємо софтом, не апаратним NSS
    SPI2->CR2 = (7u << SPI_CR2_DS_Pos)           // розмір кадру = 8 біт
              | SPI_CR2_FRXTH;                   // поріг RXNE спрацьовує вже на 1 байті
    SPI2->CR1 |= SPI_CR1_SPE;                    // увімкнути SPI
}

// Прочитати один регістр давача.
static uint8_t l3gd20_read(uint8_t reg) {
    cs_low();
    spi_xfer(reg | SPI_READ);                    // командний байт: читаю цей регістр
    uint8_t v = spi_xfer(0xFF);                  // «холостий» байт — щоб дати такт для відповіді
    cs_high();
    return v;
}

// Прочитати одразу три осі (6 байтів) з авто-інкрементом адреси.
static void l3gd20_read_xyz(int16_t *x, int16_t *y, int16_t *z) {
    uint8_t b[6];
    cs_low();
    spi_xfer(L3GD20_OUT_X_L | SPI_READ | SPI_AUTOINC);   // 0x28 | 0x80 | 0x40 = 0xE8
    for (int i = 0; i < 6; i++) b[i] = spi_xfer(0xFF);
    cs_high();
    // Кожна вісь — 16 біт, молодший байт першим (little-endian).
    *x = (int16_t)((b[1] << 8) | b[0]);
    *y = (int16_t)((b[3] << 8) | b[2]);
    *z = (int16_t)((b[5] << 8) | b[4]);
}
