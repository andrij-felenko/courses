#include "flash_map.h"

/* Регістровий блок контролера пам'яті STM32F4 (RM0090, розділ 3.9). */
#define FLASH_R_BASE 0x40023C00u
#define FLASH_KEYR   (*(volatile uint32_t *)(FLASH_R_BASE + 0x04u))
#define FLASH_SR     (*(volatile uint32_t *)(FLASH_R_BASE + 0x0Cu))
#define FLASH_CR     (*(volatile uint32_t *)(FLASH_R_BASE + 0x10u))

#define FLASH_KEY1 0x45670123u
#define FLASH_KEY2 0xCDEF89ABu

#define FLASH_SR_EOP     (1u << 0)
#define FLASH_SR_OPERR   (1u << 1)
#define FLASH_SR_WRPERR  (1u << 4)
#define FLASH_SR_PGAERR  (1u << 5)
#define FLASH_SR_PGPERR  (1u << 6)
#define FLASH_SR_PGSERR  (1u << 7)
#define FLASH_SR_BSY     (1u << 16)
#define FLASH_SR_ERRORS  (FLASH_SR_OPERR | FLASH_SR_WRPERR | FLASH_SR_PGAERR | \
                          FLASH_SR_PGPERR | FLASH_SR_PGSERR)

#define FLASH_CR_PG      (1u << 0)
#define FLASH_CR_SER     (1u << 1)
#define FLASH_CR_SNB_MSK (0x1Fu << 3)
#define FLASH_CR_PSIZE   (0x3u << 8)
#define FLASH_CR_PSIZE_X8 (0x0u << 8) /* Побайтний запис працює від 1.8 В */
#define FLASH_CR_STRT    (1u << 16)
#define FLASH_CR_LOCK    (1u << 31)

/* Межі SRAM STM32F405 — за ними перевіряємо вектор початкового стека. */
#define SRAM_BASE 0x20000000u
#define SRAM_END  0x20020000u

static const flash_sector_t sectors[] = {
    { 0x08000000u,  16u * 1024u,  0u, FLASH_ACC_READ },
    { 0x08004000u,  16u * 1024u,  1u, FLASH_ACC_READ },
    { 0x08008000u,  16u * 1024u,  2u, FLASH_ACC_READ | FLASH_ACC_ERASE | FLASH_ACC_WRITE },
    { 0x0800C000u,  16u * 1024u,  3u, FLASH_ACC_READ | FLASH_ACC_ERASE | FLASH_ACC_WRITE },
    { 0x08010000u,  64u * 1024u,  4u, FLASH_ACC_READ | FLASH_ACC_ERASE | FLASH_ACC_WRITE },
    { 0x08020000u, 128u * 1024u,  5u, FLASH_ACC_READ | FLASH_ACC_ERASE | FLASH_ACC_WRITE },
    { 0x08040000u, 128u * 1024u,  6u, FLASH_ACC_READ | FLASH_ACC_ERASE | FLASH_ACC_WRITE },
    { 0x08060000u, 128u * 1024u,  7u, FLASH_ACC_READ | FLASH_ACC_ERASE | FLASH_ACC_WRITE },
    { 0x08080000u, 128u * 1024u,  8u, FLASH_ACC_READ | FLASH_ACC_ERASE | FLASH_ACC_WRITE },
    { 0x080A0000u, 128u * 1024u,  9u, FLASH_ACC_READ | FLASH_ACC_ERASE | FLASH_ACC_WRITE },
    { 0x080C0000u, 128u * 1024u, 10u, FLASH_ACC_READ | FLASH_ACC_ERASE | FLASH_ACC_WRITE },
    { 0x080E0000u, 128u * 1024u, 11u, FLASH_ACC_READ | FLASH_ACC_ERASE | FLASH_ACC_WRITE }
};

#define SECTOR_COUNT (sizeof(sectors) / sizeof(sectors[0]))

const flash_sector_t *flash_map_sector_at(uint32_t address)
{
    size_t i;
    for (i = 0u; i < SECTOR_COUNT; ++i) {
        if (address >= sectors[i].address &&
            address < sectors[i].address + sectors[i].size) {
            return &sectors[i];
        }
    }
    return NULL;
}

int flash_map_is_app_range(uint32_t address, size_t length)
{
    uint32_t end;

    if (length == 0u) {
        return 0;
    }
    /* Переповнення адреси ловимо до порівнянь. */
    if (address > UINT32_MAX - (uint32_t)length) {
        return 0;
    }
    end = address + (uint32_t)length;
    return (address >= FLASH_APP_BASE) &&
           (end <= FLASH_BASE_ADDR + FLASH_TOTAL_SIZE);
}

uint32_t flash_map_erase_timeout_ms(const flash_sector_t *sector)
{
    if (sector == NULL) {
        return 0u;
    }
    /* Довідник дає typ/max на стирання сектора; віддаємо хостові верхню оцінку. */
    if (sector->size <= 16u * 1024u) {
        return 800u;
    }
    if (sector->size <= 64u * 1024u) {
        return 1600u;
    }
    return 3000u;
}

uint32_t flash_map_app_erase_timeout_ms(void)
{
    uint32_t total = 0u;
    size_t i;

    for (i = 0u; i < SECTOR_COUNT; ++i) {
        if ((sectors[i].access & FLASH_ACC_ERASE) != 0u) {
            total += flash_map_erase_timeout_ms(&sectors[i]);
        }
    }
    return total;
}

/* --- Складання рядка карти пам'яті ------------------------------------- */
/* Форматуємо руками: тягнути snprintf у завантажувач, якому відведено
   32 КБ, невигідно — бібліотечний форматувальник з'їдає кілька кілобайтів. */

static size_t append_str(char *out, size_t cap, size_t pos, const char *text)
{
    while (*text != '\0') {
        if (pos + 1u >= cap) {
            return cap; /* мітка переповнення */
        }
        out[pos++] = *text++;
    }
    return pos;
}

static size_t append_dec(char *out, size_t cap, size_t pos, uint32_t value, unsigned width)
{
    char tmp[10];
    unsigned n = 0u;

    do {
        tmp[n++] = (char)('0' + (value % 10u));
        value /= 10u;
    } while (value != 0u && n < sizeof tmp);

    while (n < width && n < sizeof tmp) {
        tmp[n++] = '0'; /* доповнення нулями зліва: 4 -> "04" */
    }

    while (n > 0u) {
        if (pos + 1u >= cap) {
            return cap;
        }
        out[pos++] = tmp[--n];
    }
    return pos;
}

static size_t append_hex32(char *out, size_t cap, size_t pos, uint32_t value)
{
    static const char digits[] = "0123456789ABCDEF";
    int shift;

    for (shift = 28; shift >= 0; shift -= 4) {
        if (pos + 1u >= cap) {
            return cap;
        }
        out[pos++] = digits[(value >> shift) & 0xFu];
    }
    return pos;
}

static char access_letter(uint8_t mask)
{
    /* DfuSe кодує права літерою: 'a' = лише читання ... 'g' = read+write+erase. */
    return (char)('a' - 1 + (mask & 0x7u));
}

size_t flash_map_layout_string(char *out, size_t cap)
{
    size_t pos;
    size_t i = 0u;
    int first = 1;

    if (out == NULL || cap == 0u) {
        return 0u;
    }

    pos = append_str(out, cap, 0u, "@Internal Flash  /0x");
    pos = append_hex32(out, cap, pos, FLASH_BASE_ADDR);
    pos = append_str(out, cap, pos, "/");

    while (i < SECTOR_COUNT) {
        /* Групуємо підряд ідентичні сектори: однаковий розмір і однакові права. */
        size_t n = 1u;
        while (i + n < SECTOR_COUNT &&
               sectors[i + n].size == sectors[i].size &&
               sectors[i + n].access == sectors[i].access) {
            ++n;
        }

        if (!first) {
            pos = append_str(out, cap, pos, ",");
        }
        first = 0;

        pos = append_dec(out, cap, pos, (uint32_t)n, 2u);
        pos = append_str(out, cap, pos, "*");
        pos = append_dec(out, cap, pos, sectors[i].size / 1024u, 3u);
        pos = append_str(out, cap, pos, "K");
        if (pos + 1u < cap) {
            out[pos++] = access_letter(sectors[i].access);
        } else {
            pos = cap;
        }

        i += n;
    }

    if (pos >= cap) {
        return 0u; /* не влізло — краще віддати порожньо, ніж обрізок */
    }
    out[pos] = '\0';
    return pos;
}

size_t flash_map_layout_descriptor(uint8_t *out, size_t cap)
{
    char text[96];
    size_t n;
    size_t total;
    size_t i;

    n = flash_map_layout_string(text, sizeof text);
    if (n == 0u || out == NULL) {
        return 0u;
    }

    /* USB String Descriptor: bLength, bDescriptorType = 0x03, далі UTF-16LE. */
    total = 2u + 2u * n;
    if (total > 255u || total > cap) {
        return 0u;
    }

    out[0] = (uint8_t)total;
    out[1] = 0x03u;
    for (i = 0u; i < n; ++i) {
        out[2u + 2u * i] = (uint8_t)text[i];
        out[3u + 2u * i] = 0u;
    }
    return total;
}

/* --- Фізичні операції над пам'яттю -------------------------------------- */

static void flash_unlock(void)
{
    if ((FLASH_CR & FLASH_CR_LOCK) != 0u) {
        FLASH_KEYR = FLASH_KEY1;
        FLASH_KEYR = FLASH_KEY2;
    }
}

static void flash_lock(void)
{
    FLASH_CR |= FLASH_CR_LOCK;
}

static void flash_clear_errors(void)
{
    FLASH_SR = FLASH_SR_EOP | FLASH_SR_ERRORS; /* запис одиниці скидає прапорець */
}

static dfu_status_t flash_wait(void)
{
    uint32_t sr;

    while ((FLASH_SR & FLASH_SR_BSY) != 0u) {
        /* Порожнє очікування: під час запису ядро все одно стоїть на шині. */
    }

    sr = FLASH_SR;
    flash_clear_errors();

    if ((sr & FLASH_SR_WRPERR) != 0u) {
        return DFU_ERR_WRITE; /* сектор під апаратним захистом запису */
    }
    if ((sr & (FLASH_SR_PGAERR | FLASH_SR_PGPERR | FLASH_SR_PGSERR)) != 0u) {
        return DFU_ERR_PROG;
    }
    if ((sr & FLASH_SR_OPERR) != 0u) {
        return DFU_ERR_ERASE;
    }
    return DFU_OK;
}

dfu_status_t flash_erase_sector(uint32_t address)
{
    const flash_sector_t *sector = flash_map_sector_at(address);
    dfu_status_t status;

    if (sector == NULL) {
        return DFU_ERR_ADDRESS;
    }
    if ((sector->access & FLASH_ACC_ERASE) == 0u) {
        /* Сектори самого завантажувача хост стерти не може — інакше
           після обриву живлення платі нічим буде стартувати. */
        return DFU_ERR_TARGET;
    }

    flash_unlock();
    status = flash_wait();
    if (status != DFU_OK) {
        flash_lock();
        return status;
    }

    FLASH_CR &= ~(FLASH_CR_SNB_MSK | FLASH_CR_PSIZE);
    FLASH_CR |= FLASH_CR_SER | FLASH_CR_PSIZE_X8 |
                ((uint32_t)sector->index << 3);
    FLASH_CR |= FLASH_CR_STRT;

    status = flash_wait();
    FLASH_CR &= ~(FLASH_CR_SER | FLASH_CR_SNB_MSK);
    flash_lock();
    return status;
}

dfu_status_t flash_erase_application(void)
{
    size_t i;

    /* Справжнього Mass Erase не робимо: він змів би й завантажувач. */
    for (i = 0u; i < SECTOR_COUNT; ++i) {
        if ((sectors[i].access & FLASH_ACC_ERASE) != 0u) {
            dfu_status_t status = flash_erase_sector(sectors[i].address);
            if (status != DFU_OK) {
                return status;
            }
        }
    }
    return DFU_OK;
}

dfu_status_t flash_program(uint32_t address, const uint8_t *data, size_t length)
{
    dfu_status_t status;
    size_t i;

    if (data == NULL || !flash_map_is_app_range(address, length)) {
        return DFU_ERR_ADDRESS;
    }

    flash_unlock();
    status = flash_wait();
    if (status != DFU_OK) {
        flash_lock();
        return status;
    }

    FLASH_CR &= ~FLASH_CR_PSIZE;
    FLASH_CR |= FLASH_CR_PSIZE_X8 | FLASH_CR_PG;

    for (i = 0u; i < length; ++i) {
        *(volatile uint8_t *)(address + i) = data[i];
        status = flash_wait();
        if (status != DFU_OK) {
            break;
        }
        /* Перевіряємо одразу: помилка запису не завжди піднімає прапорець. */
        if (*(volatile uint8_t *)(address + i) != data[i]) {
            status = DFU_ERR_VERIFY;
            break;
        }
    }

    FLASH_CR &= ~FLASH_CR_PG;
    flash_lock();
    return status;
}

const uint8_t *flash_read(uint32_t address, size_t length)
{
    uint32_t end;

    if (length == 0u || address < FLASH_BASE_ADDR) {
        return NULL;
    }
    if (address > UINT32_MAX - (uint32_t)length) {
        return NULL;
    }
    end = address + (uint32_t)length;
    if (end > FLASH_BASE_ADDR + FLASH_TOTAL_SIZE) {
        return NULL;
    }
    /* Flash відображена в адресний простір — віддаємо вказівник без копії. */
    return (const uint8_t *)address;
}

int flash_app_image_valid(void)
{
    const uint32_t *vectors = (const uint32_t *)FLASH_APP_BASE;
    uint32_t stack_top = vectors[0];
    uint32_t reset_pc  = vectors[1];

    if (stack_top < SRAM_BASE || stack_top > SRAM_END) {
        return 0; /* стер образ або записали сміття */
    }
    if (reset_pc < FLASH_APP_BASE ||
        reset_pc >= FLASH_BASE_ADDR + FLASH_TOTAL_SIZE) {
        return 0;
    }
    /* Cortex-M виконує лише Thumb: молодший біт вектора Reset мусить бути 1. */
    return ((reset_pc & 1u) != 0u) ? 1 : 0;
}
