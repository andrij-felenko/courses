/* SSD1306 128x64 на SPI1: PA5 = SCK, PA7 = MOSI, PA4 = CS, PA1 = D/C, PA2 = RES.
   Шина навмисно повільна (fPCLK/64 = 250 кГц): модуль висить на шлейфі, і це
   типовий компроміс. Наслідок рахується просто: 1024 байти по 9 тактів на біт
   дають ≈ 33 мс на кадр — та сама блокуюча ділянка, через яку валиться все інше. */
#include "display.h"

#include "stm32g0xx.h"

#define FB_PAGES 8u
#define FB_COLS  128u

static uint8_t s_fb[FB_PAGES * FB_COLS];

/* Цифри 3x5: кожен байт — стовпчик, біт 0 угорі. */
static const uint8_t k_font[10][3] = {
    {0x1F, 0x11, 0x1F}, {0x02, 0x1F, 0x00}, {0x19, 0x15, 0x17}, {0x11, 0x15, 0x1F},
    {0x07, 0x04, 0x1F}, {0x17, 0x15, 0x1D}, {0x1F, 0x15, 0x1C}, {0x01, 0x01, 0x1F},
    {0x1F, 0x15, 0x1F}, {0x07, 0x15, 0x1F},
};

static void cs(bool active)  { if (active) GPIOA->BSRR = GPIO_BSRR_BR4; else GPIOA->BSRR = GPIO_BSRR_BS4; }
static void dc(bool data)    { if (data)   GPIOA->BSRR = GPIO_BSRR_BS1; else GPIOA->BSRR = GPIO_BSRR_BR1; }

static bool spi_write(const uint8_t *buf, uint32_t len)
{
    for (uint32_t i = 0; i < len; i++) {
        uint32_t guard = 100000u;
        while ((SPI1->SR & SPI_SR_TXE) == 0u) {
            if (guard-- == 0u) {
                return false; /* шина мовчить — далі не сліпнемо в циклі */
            }
        }
        *(volatile uint8_t *)&SPI1->DR = buf[i];
    }
    /* Кадр не закінчено, поки зсувний регістр не спорожнів. */
    uint32_t guard = 100000u;
    while (((SPI1->SR & SPI_SR_BSY) != 0u) && (guard-- != 0u)) { }
    while ((SPI1->SR & SPI_SR_RXNE) != 0u) {
        (void)*(volatile uint8_t *)&SPI1->DR; /* вичищаємо прийомний FIFO */
    }
    return guard != 0u;
}

static bool cmd(uint8_t c)
{
    dc(false);
    cs(true);
    bool ok = spi_write(&c, 1u);
    cs(false);
    return ok;
}

static void pins_init(void)
{
    RCC->IOPENR  |= RCC_IOPENR_GPIOAEN;
    RCC->APBENR2 |= RCC_APBENR2_SPI1EN;

    /* PA5/PA7 — альтернативна функція 0 (SPI1). */
    GPIOA->MODER = (GPIOA->MODER & ~(GPIO_MODER_MODE5 | GPIO_MODER_MODE7))
                 | (2u << GPIO_MODER_MODE5_Pos) | (2u << GPIO_MODER_MODE7_Pos);
    GPIOA->OSPEEDR |= (2u << GPIO_OSPEEDR_OSPEED5_Pos) | (2u << GPIO_OSPEEDR_OSPEED7_Pos);

    /* PA1, PA2, PA4 — звичайні виходи. */
    GPIOA->MODER = (GPIOA->MODER & ~(GPIO_MODER_MODE1 | GPIO_MODER_MODE2 | GPIO_MODER_MODE4))
                 | (1u << GPIO_MODER_MODE1_Pos) | (1u << GPIO_MODER_MODE2_Pos)
                 | (1u << GPIO_MODER_MODE4_Pos);
    GPIOA->BSRR = GPIO_BSRR_BS4; /* CS неактивний */

    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI | (5u << SPI_CR1_BR_Pos);
    SPI1->CR2 = SPI_CR2_DS_0 | SPI_CR2_DS_1 | SPI_CR2_DS_2 | SPI_CR2_FRXTH; /* 8 біт */
    SPI1->CR1 |= SPI_CR1_SPE;
}

bool display_init(void)
{
    static const uint8_t init_seq[] = {
        0xAE,             /* дисплей вимкнено на час налаштування */
        0xD5, 0x80,       /* тактування                            */
        0xA8, 0x3F,       /* 64 рядки                              */
        0xD3, 0x00, 0x40, /* без зсуву                             */
        0x8D, 0x14,       /* зарядна помпа від VCC логіки          */
        0x20, 0x00,       /* горизонтальна адресація               */
        0xA1, 0xC8,       /* орієнтація модуля                     */
        0xDA, 0x12, 0x81, 0x7F,
        0xD9, 0xF1, 0xDB, 0x40,
        0xA4, 0xA6, 0xAF, /* вміст RAM, пряма полярність, увімкнено */
    };

    pins_init();

    GPIOA->BSRR = GPIO_BSRR_BR2;                       /* RES низький */
    for (volatile int i = 0; i < 20000; i++) { }       /* > 3 мкс, з запасом */
    GPIOA->BSRR = GPIO_BSRR_BS2;
    for (volatile int i = 0; i < 20000; i++) { }

    for (unsigned i = 0; i < sizeof init_seq; i++) {
        if (!cmd(init_seq[i])) {
            return false;
        }
    }
    display_clear();
    return true;
}

void display_clear(void)
{
    for (unsigned i = 0; i < sizeof s_fb; i++) {
        s_fb[i] = 0u;
    }
}

static void put_col(uint8_t x, uint8_t page, uint8_t bits)
{
    if ((x < FB_COLS) && (page < FB_PAGES)) {
        s_fb[(uint32_t)page * FB_COLS + x] |= bits;
    }
}

static uint8_t digit(uint8_t x, uint8_t page, uint8_t d)
{
    for (uint8_t c = 0; c < 3u; c++) {
        put_col((uint8_t)(x + c), page, k_font[d][c]);
    }
    return (uint8_t)(x + 4u); /* 3 стовпчики + проміжок */
}

void display_number(uint8_t x, uint8_t page, int32_t value, uint8_t decimals)
{
    uint8_t buf[10];
    uint8_t n = 0u;
    uint32_t v;

    if (value < 0) {
        put_col(x, page, 0x04); /* мінус — середній рядок */
        put_col((uint8_t)(x + 1u), page, 0x04);
        x = (uint8_t)(x + 3u);
        v = (uint32_t)(-value);
    } else {
        v = (uint32_t)value;
    }

    do {
        buf[n++] = (uint8_t)(v % 10u);
        v /= 10u;
    } while ((v != 0u) && (n < sizeof buf));

    while (n <= decimals) {
        buf[n++] = 0u; /* доводимо до вигляду 0.xx */
    }

    while (n > 0u) {
        n--;
        x = digit(x, page, buf[n]);
        if ((decimals != 0u) && (n == decimals)) {
            put_col(x, page, 0x10); /* кома — нижній рядок */
            x = (uint8_t)(x + 2u);
        }
    }
}

void display_bar(uint8_t page, int32_t value, int32_t lo, int32_t hi)
{
    int32_t span = hi - lo;
    int32_t w;

    if (span <= 0) {
        return;
    }
    if (value < lo) { value = lo; }
    if (value > hi) { value = hi; }

    w = ((value - lo) * (int32_t)FB_COLS) / span;
    for (int32_t x = 0; x < w; x++) {
        put_col((uint8_t)x, page, 0x3C);
    }
}

bool display_flush(void)
{
    static const uint8_t window[] = { 0x21, 0x00, 0x7F, 0x22, 0x00, 0x07 };

    for (unsigned i = 0; i < sizeof window; i++) {
        if (!cmd(window[i])) {
            return false;
        }
    }
    dc(true);
    cs(true);
    bool ok = spi_write(s_fb, sizeof s_fb);
    cs(false);
    return ok;
}
