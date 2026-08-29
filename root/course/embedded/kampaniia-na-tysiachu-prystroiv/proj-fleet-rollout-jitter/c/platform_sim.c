/* Хостова реалізація апаратних гачків.
 *
 * Flash — масив, у якому запис уміє лише гасити біти (як у справжньому кристалі),
 * а стирання повертає сторінку в 0xFF. Backup-регістри — статичний масив: він
 * переживає симульоване перезавантаження рівно так само, як справжні регістри
 * переживають скидання ядра. */
#include "platform.h"

#include <stdlib.h>
#include <string.h>
#include <time.h>

static uint32_t s_bkp[PLAT_BKP_WORDS];
static uint8_t  s_flash[PLAT_FLASH_SIZE];
static bool     s_flash_ready;
static bool     s_flash_unlocked;
static bool     s_reboot_requested;
static uint64_t s_uptime_ms;

static void flash_lazy_init(void)
{
    if (!s_flash_ready) {
        memset(s_flash, 0xFF, sizeof(s_flash));
        s_flash_ready = true;
    }
}

uint32_t plat_bkp_read(unsigned idx)
{
    return (idx < PLAT_BKP_WORDS) ? s_bkp[idx] : 0u;
}

void plat_bkp_write(unsigned idx, uint32_t value)
{
    if (idx < PLAT_BKP_WORDS) {
        s_bkp[idx] = value;
    }
}

/* На платі це справжній TRNG; тут — джерело, якого досить для показу, що
 * різні вузли розходяться в часі. Ключів на цьому генераторі не роблять. */
uint32_t plat_trng_word(void)
{
    static uint64_t state;
    if (state == 0) {
        state = (uint64_t)time(NULL) ^ ((uint64_t)(uintptr_t)&state << 16);
    }
    state = state * 6364136223846793005ull + 1442695040888963407ull;
    return (uint32_t)(state >> 33);
}

uint32_t plat_adc_noise_word(void)
{
    /* Плата без вільного аналогового входу — джерела просто немає. */
    return 0u;
}

uint32_t plat_timer_jitter_word(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        return 0u;
    }
    return (uint32_t)ts.tv_nsec;
}

uint64_t plat_uptime_ms(void)
{
    return s_uptime_ms;
}

/* У симуляції час не спимо, а просто просуваємо: кампанія розтягнута на години,
 * і чекати їх насправді немає сенсу. */
void plat_delay_ms(uint32_t ms)
{
    s_uptime_ms += ms;
}

bool plat_flash_unlock(void)
{
    flash_lazy_init();
    s_flash_unlocked = true;
    return true;
}

void plat_flash_lock(void)
{
    s_flash_unlocked = false;
}

bool plat_flash_erase_page(uint32_t addr)
{
    flash_lazy_init();
    if (!s_flash_unlocked) {
        return false;
    }
    if (addr % PLAT_FLASH_PAGE != 0) {
        return false;
    }
    if (addr < PLAT_FLASH_BASE || addr + PLAT_FLASH_PAGE > PLAT_FLASH_BASE + PLAT_FLASH_SIZE) {
        return false;
    }
    memset(&s_flash[addr - PLAT_FLASH_BASE], 0xFF, PLAT_FLASH_PAGE);
    return true;
}

bool plat_flash_program(uint32_t addr, const uint8_t *data, size_t len)
{
    flash_lazy_init();
    if (!s_flash_unlocked || data == NULL) {
        return false;
    }
    if (addr % PLAT_FLASH_WORD != 0 || len % PLAT_FLASH_WORD != 0) {
        return false;
    }
    if (addr < PLAT_FLASH_BASE || addr + len > PLAT_FLASH_BASE + PLAT_FLASH_SIZE) {
        return false;
    }

    uint8_t *dst = &s_flash[addr - PLAT_FLASH_BASE];
    for (size_t i = 0; i < len; ++i) {
        /* Запис у нестерту комірку в кристалі дає помилку PGSERR, а не мовчазне
         * псування — повторюємо цю поведінку, інакше вона спливе вже в полі. */
        if ((dst[i] & data[i]) != data[i]) {
            return false;
        }
        dst[i] &= data[i];
    }
    return true;
}

const uint8_t *plat_flash_ptr(uint32_t addr)
{
    flash_lazy_init();
    if (addr < PLAT_FLASH_BASE || addr >= PLAT_FLASH_BASE + PLAT_FLASH_SIZE) {
        return NULL;
    }
    return &s_flash[addr - PLAT_FLASH_BASE];
}

void plat_hardware_id(uint8_t out[16])
{
    /* Серійний номер цього вузла парку. На кристалі — читання з 0x1FFF7A10. */
    static const uint8_t uid[16] = {
        0x30, 0x54, 0x35, 0x51, 0x33, 0x37, 0x39, 0x31,
        0x00, 0x27, 0x00, 0x1B, 0x00, 0x00, 0x00, 0x00
    };
    memcpy(out, uid, sizeof(uid));
}

void plat_reboot(void)
{
    s_reboot_requested = true;
}

bool plat_sim_take_reboot(void)
{
    bool r = s_reboot_requested;
    s_reboot_requested = false;
    return r;
}
