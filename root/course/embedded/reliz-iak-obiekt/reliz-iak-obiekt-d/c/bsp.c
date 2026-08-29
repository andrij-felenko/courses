#include "bsp.h"

#include <string.h>

/* Прив'язка до заліза: STM32F4, доступ прямо до регістрів. CMSIS сюди не
   тягнемо — завантажувач мусить лишатися малим і самодостатнім. */

#define REG32(addr)      (*(volatile uint32_t *)(addr))

#define RCC_BASE         0x40023800u
#define RCC_AHB1ENR      REG32(RCC_BASE + 0x30u)

#define GPIOB_BASE       0x40020400u
#define GPIOB_MODER      REG32(GPIOB_BASE + 0x00u)
#define GPIOB_PUPDR      REG32(GPIOB_BASE + 0x0Cu)
#define GPIOB_IDR        REG32(GPIOB_BASE + 0x10u)

#define GPIOC_BASE       0x40020800u
#define GPIOC_MODER      REG32(GPIOC_BASE + 0x00u)
#define GPIOC_BSRR       REG32(GPIOC_BASE + 0x18u)

#define FLASH_R_BASE     0x40023C00u
#define FLASH_KEYR       REG32(FLASH_R_BASE + 0x04u)
#define FLASH_SR         REG32(FLASH_R_BASE + 0x0Cu)
#define FLASH_CR         REG32(FLASH_R_BASE + 0x10u)

#define FLASH_KEY1       0x45670123u
#define FLASH_KEY2       0xCDEF89ABu

#define FLASH_SR_BSY     (1u << 16)
#define FLASH_SR_ERRORS  ((1u << 7) | (1u << 6) | (1u << 5) | (1u << 4) | (1u << 1))
#define FLASH_SR_EOP     (1u << 0)
#define FLASH_CR_PG      (1u << 0)
#define FLASH_CR_PSIZE   (3u << 8)
#define FLASH_CR_LOCK    (1u << 31)

/* OTP-блок STM32F4: 16 блоків по 32 байти від 0x1FFF7800, байти блокування —
   від 0x1FFF7A00. Блок 0 тримає лічильник безпеки, блок 1 — кореневий ключ
   (його байт блокування завод пропалює одразу після персоналізації). */
#define OTP_BASE         0x1FFF7800u
#define OTP_BLOCK_SIZE   32u
#define OTP_COUNTER      (OTP_BASE + 0u * OTP_BLOCK_SIZE)
#define OTP_ROOT_KEY     (OTP_BASE + 1u * OTP_BLOCK_SIZE)

/* Ревізія плати: три виводи PB12..PB14. Зовнішні резистори 10 кОм тягнуть
   кожен вивід до 3.3 В або до землі; усередині вмикаємо слабку (≈40 кОм)
   підтяжку до землі, щоб нерозпаяний вивід читався як нуль, а не плавав.
   Зовнішні 10 кОм до живлення перебивають її з запасом: 3.3 · 40/50 ≈ 2.6 В,
   а це впевнена логічна одиниця. */
#define REV_PIN_FIRST    12u
#define REV_PIN_COUNT    3u

#define LED_PIN          13u   /* PC13 */

void bsp_early_init(void)
{
    volatile uint32_t settle;

    RCC_AHB1ENR |= (1u << 1) | (1u << 2);   /* такт на GPIOB і GPIOC */

    for (unsigned i = 0; i < REV_PIN_COUNT; i++) {
        const unsigned pin = REV_PIN_FIRST + i;
        GPIOB_MODER &= ~(3u << (2u * pin));           /* вхід */
        GPIOB_PUPDR &= ~(3u << (2u * pin));
        GPIOB_PUPDR |=  (2u << (2u * pin));           /* підтяжка до землі */
    }

    GPIOC_MODER &= ~(3u << (2u * LED_PIN));
    GPIOC_MODER |=  (1u << (2u * LED_PIN));           /* вихід push-pull */

    /* Підтяжка з ємністю виводу дає сталу в одиниці мікросекунд —
       читати одразу після налаштування не можна. */
    for (settle = 0; settle < 2000u; settle++) {
    }
}

uint32_t bsp_hw_platform_id(void)
{
    return BSP_HW_PLATFORM_ID;
}

uint8_t bsp_pcb_revision(void)
{
    const uint32_t idr = GPIOB_IDR;
    uint8_t rev = 0u;

    for (unsigned i = 0; i < REV_PIN_COUNT; i++) {
        const unsigned pin = REV_PIN_FIRST + i;
        if ((idr & (1u << pin)) != 0u) {
            rev |= (uint8_t)(1u << i);
        }
    }
    return rev;
}

const uint8_t *bsp_root_public_key(void)
{
    const uint8_t *key = (const uint8_t *)OTP_ROOT_KEY;

    /* Незаписана OTP — суцільні 0xFF. Такий «ключ» узяти за кореневий
       означало б перевіряти підпис проти сміття, тому кажемо чесно: ключа
       немає. Плата не пройшла заводську персоналізацію. */
    for (unsigned i = 0; i < 32u; i++) {
        if (key[i] != 0xFFu) {
            return key;
        }
    }
    return 0;
}

uint32_t bsp_security_counter(void)
{
    const uint8_t *cells = (const uint8_t *)OTP_COUNTER;
    uint32_t level = 0u;

    /* Термометровий код: рівень — це кількість пропалених у нуль байтів.
       Максимум 32 підвищення безпеки за життя виробу. */
    for (unsigned i = 0; i < OTP_BLOCK_SIZE; i++) {
        if (cells[i] == 0x00u) {
            level++;
        }
    }
    return level;
}

static int flash_wait_idle(void)
{
    while ((FLASH_SR & FLASH_SR_BSY) != 0u) {
    }
    if ((FLASH_SR & FLASH_SR_ERRORS) != 0u) {
        FLASH_SR = FLASH_SR_ERRORS | FLASH_SR_EOP;   /* прапорці скидаються записом одиниці */
        return -1;
    }
    return 0;
}

static int flash_program_byte(uint32_t address, uint8_t value)
{
    if (flash_wait_idle() != 0) {
        return -1;
    }

    FLASH_CR &= ~FLASH_CR_PSIZE;      /* PSIZE = 00: програмуємо побайтно */
    FLASH_CR |= FLASH_CR_PG;
    *(volatile uint8_t *)address = value;

    if (flash_wait_idle() != 0) {
        FLASH_CR &= ~FLASH_CR_PG;
        return -1;
    }
    FLASH_CR &= ~FLASH_CR_PG;

    /* Читаємо назад: OTP пропалюється один раз, і мовчазна невдача тут
       означала б пристрій, який назавжди приймає старі версії. */
    return (*(volatile uint8_t *)address == value) ? 0 : -1;
}

int bsp_security_counter_commit(uint32_t level)
{
    uint32_t current = bsp_security_counter();
    int rc = 0;

    if (level > OTP_BLOCK_SIZE) {
        return -1;                     /* більше рівнів чип не вміє */
    }
    if (level <= current) {
        return 0;                      /* уже на цьому рівні — нічого палити */
    }

    if ((FLASH_CR & FLASH_CR_LOCK) != 0u) {
        FLASH_KEYR = FLASH_KEY1;
        FLASH_KEYR = FLASH_KEY2;
        if ((FLASH_CR & FLASH_CR_LOCK) != 0u) {
            return -1;                 /* послідовність відкриття не спрацювала */
        }
    }

    for (; current < level && rc == 0; current++) {
        rc = flash_program_byte(OTP_COUNTER + current, 0x00u);
    }

    FLASH_CR |= FLASH_CR_LOCK;
    return rc;
}

int bsp_flash_read(uint32_t address, void *dst, size_t len)
{
    /* Внутрішня Flash відображена в адресний простір, тож читання — це
       memcpy. Межі все одно перевіряємо: payload_size приходить із файлу,
       якому ми ще не довіряємо. */
    if (address < BSP_FLASH_BASE) {
        return -1;
    }
    if (len > BSP_FLASH_SIZE || address - BSP_FLASH_BASE > BSP_FLASH_SIZE - len) {
        return -1;
    }
    memcpy(dst, (const void *)(uintptr_t)address, len);
    return 0;
}

void bsp_led(int on)
{
    /* BSRR: молодша половина вмикає, старша скидає — без read-modify-write. */
    GPIOC_BSRR = on ? (1u << LED_PIN) : (1u << (LED_PIN + 16u));
}

void bsp_delay_ms(uint32_t ms)
{
    /* Завантажувач працює на HSI 16 МГц до будь-якого налаштування PLL.
       Точності тут не треба: затримка потрібна лише миготінню й підтяжкам. */
    volatile uint32_t i;
    while (ms-- > 0u) {
        for (i = 0; i < 1600u; i++) {
        }
    }
}
