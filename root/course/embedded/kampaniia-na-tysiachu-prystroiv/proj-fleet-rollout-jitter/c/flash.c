#include "flash.h"

#include "platform.h"

#include <string.h>

/* Функція, яку лінкер кладе в RAM. На хості атрибут ні до чого. */
#if defined(__arm__)
#  define OTA_RAMFUNC __attribute__((section(".RamFunc"), noinline))
#else
#  define OTA_RAMFUNC
#endif

#define STATE_MAGIC     0x4F544131u   /* 'O','T','A','1' */
#define STATE_WORDS     8u            /* 7 слів даних + CRC                     */
#define STATE_SLOTS     2u            /* два слоти: запис не псує чинного стану */
#define STATE_REC_BYTES (STATE_WORDS * 4u)

#define JOURNAL_BASE  NVRAM_BASE
#define JOURNAL_LIMIT (NVRAM_BASE + PLAT_FLASH_PAGE)   /* одна сторінка журналу */

uint32_t crc32_update(uint32_t crc, const uint8_t *data, size_t len)
{
    crc = ~crc;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (unsigned bit = 0; bit < 8; ++bit) {
            const uint32_t mask = (uint32_t)0 - (crc & 1u);
            crc = (crc >> 1) ^ (0xEDB88320u & mask);
        }
    }
    return ~crc;
}

/* ---- пакування запису ---------------------------------------------------- */

static void state_pack(const ota_state_t *st, uint32_t w[STATE_WORDS])
{
    w[0] = STATE_MAGIC;
    w[1] = ((uint32_t)st->seq << 24) |
           ((uint32_t)(st->active_bank & 1u) << 16) |
           ((uint32_t)(st->trial_pending ? 1u : 0u) << 8) |
           (uint32_t)st->boot_failures;
    w[2] = st->campaign_id;
    w[3] = st->bank_len[0];
    w[4] = st->bank_crc[0];
    w[5] = st->bank_len[1];
    w[6] = st->bank_crc[1];
    w[7] = crc32_update(0u, (const uint8_t *)w, 7u * 4u);
}

static bool state_unpack(const uint32_t w[STATE_WORDS], ota_state_t *out)
{
    if (w[0] != STATE_MAGIC) {
        return false;
    }
    if (w[7] != crc32_update(0u, (const uint8_t *)w, 7u * 4u)) {
        return false;
    }
    out->seq           = (uint8_t)(w[1] >> 24);
    out->active_bank   = ((w[1] >> 16) & 1u) ? BOOT_BANK_B : BOOT_BANK_A;
    out->trial_pending = ((w[1] >> 8) & 1u) != 0u;
    out->boot_failures = (uint8_t)(w[1] & 0xFFu);
    out->campaign_id   = w[2];
    out->bank_len[0]   = w[3];
    out->bank_crc[0]   = w[4];
    out->bank_len[1]   = w[5];
    out->bank_crc[1]   = w[6];
    return true;
}

/* Порівняння версій із урахуванням переповнення лічильника (uint8). */
static bool seq_newer(uint8_t a, uint8_t b)
{
    return (int8_t)(a - b) > 0;
}

/* ---- backup-регістри ------------------------------------------------------ */

static bool bkp_slot_read(unsigned slot, ota_state_t *out)
{
    uint32_t w[STATE_WORDS];
    for (unsigned i = 0; i < STATE_WORDS; ++i) {
        w[i] = plat_bkp_read(slot * STATE_WORDS + i);
    }
    return state_unpack(w, out);
}

static void bkp_slot_write(unsigned slot, const ota_state_t *st)
{
    uint32_t w[STATE_WORDS];
    state_pack(st, w);
    for (unsigned i = 0; i < STATE_WORDS; ++i) {
        plat_bkp_write(slot * STATE_WORDS + i, w[i]);
    }
}

/* ---- журнал у секторі NVRAM ---------------------------------------------- */

static bool journal_read_latest(ota_state_t *out)
{
    bool found = false;
    ota_state_t best;

    for (uint32_t addr = JOURNAL_BASE; addr < JOURNAL_LIMIT; addr += STATE_REC_BYTES) {
        const uint8_t *p = plat_flash_ptr(addr);
        if (p == NULL) {
            break;
        }
        uint32_t w[STATE_WORDS];
        memcpy(w, p, sizeof(w));
        if (w[0] == 0xFFFFFFFFu) {
            break;      /* далі — незаписаний хвіст сторінки */
        }
        ota_state_t candidate;
        if (!state_unpack(w, &candidate)) {
            continue;   /* обірваний запис: живлення зникло під час програмування */
        }
        if (!found || seq_newer(candidate.seq, best.seq)) {
            best = candidate;
            found = true;
        }
    }

    if (found) {
        *out = best;
    }
    return found;
}

static bool journal_append(const ota_state_t *st)
{
    uint32_t addr = JOURNAL_BASE;
    while (addr < JOURNAL_LIMIT) {
        const uint8_t *p = plat_flash_ptr(addr);
        if (p == NULL) {
            return false;
        }
        uint32_t magic;
        memcpy(&magic, p, sizeof(magic));
        if (magic == 0xFFFFFFFFu) {
            break;
        }
        addr += STATE_REC_BYTES;
    }

    if (!plat_flash_unlock()) {
        return false;
    }

    bool ok = true;
    if (addr >= JOURNAL_LIMIT) {
        /* Сторінка заповнена. Стираємо й пишемо з початку: чинний стан на цей
         * момент уже лежить у backup-регістрах, тож вікно без журналу безпечне. */
        ok = plat_flash_erase_page(JOURNAL_BASE);
        addr = JOURNAL_BASE;
    }

    if (ok) {
        uint32_t w[STATE_WORDS];
        state_pack(st, w);
        ok = plat_flash_program(addr, (const uint8_t *)w, sizeof(w));
    }

    plat_flash_lock();
    return ok;
}

/* ---- відкритий інтерфейс -------------------------------------------------- */

void ota_state_load(ota_state_t *out)
{
    ota_state_t best;
    bool found = false;

    for (unsigned slot = 0; slot < STATE_SLOTS; ++slot) {
        ota_state_t candidate;
        if (bkp_slot_read(slot, &candidate)) {
            if (!found || seq_newer(candidate.seq, best.seq)) {
                best = candidate;
                found = true;
            }
        }
    }

    if (!found) {
        /* Живлення зникало: backup-регістри чисті. Піднімаємо стан із Flash. */
        found = journal_read_latest(&best);
    }

    if (found) {
        *out = best;
        return;
    }

    /* Перший старт виробу з конвеєра. */
    memset(out, 0, sizeof(*out));
    out->active_bank = BOOT_BANK_A;
}

bool ota_state_store(ota_state_t *st)
{
    st->seq++;

    /* Пишемо в слот, який НЕ був чинним: якщо живлення зникне посеред запису,
     * попередній слот лишається цілим і читабельним. */
    ota_state_t current;
    unsigned target = 0;
    if (bkp_slot_read(0, &current)) {
        ota_state_t other;
        if (!bkp_slot_read(1, &other) || seq_newer(current.seq, other.seq)) {
            target = 1;
        }
    }

    bkp_slot_write(target, st);
    return journal_append(st);
}

uint32_t flash_bank_base(boot_bank_t bank)
{
    return (bank == BOOT_BANK_B) ? BANK_B_BASE : BANK_A_BASE;
}

boot_bank_t flash_other_bank(boot_bank_t bank)
{
    return (bank == BOOT_BANK_B) ? BOOT_BANK_A : BOOT_BANK_B;
}

bool flash_bank_erase(boot_bank_t bank)
{
    const uint32_t base = flash_bank_base(bank);

    if (!plat_flash_unlock()) {
        return false;
    }
    bool ok = true;
    for (uint32_t off = 0; off < BANK_SIZE && ok; off += PLAT_FLASH_PAGE) {
        ok = plat_flash_erase_page(base + off);
    }
    plat_flash_lock();
    return ok;
}

OTA_RAMFUNC
static bool bank_program_from_ram(uint32_t addr, const uint8_t *data, size_t len)
{
    /* Уся ця функція виконується з RAM. Переривання тут не заборонені, але
     * їхні обробники теж мусять бути в RAM — інакше перше ж переривання під
     * час запису зупинить ядро на шині Flash. */
    return plat_flash_program(addr, data, len);
}

bool flash_bank_write(boot_bank_t bank, uint32_t offset, const uint8_t *data, size_t len)
{
    if (data == NULL || len == 0) {
        return false;
    }
    if (offset % PLAT_FLASH_WORD != 0) {
        return false;
    }
    if (offset > BANK_SIZE || len > BANK_SIZE - offset) {
        return false;   /* образ більший за банк — далі йти немає куди */
    }

    const uint32_t addr = flash_bank_base(bank) + offset;

    /* Хвіст, коротший за квант запису, доповнюємо 0xFF: у стертій Flash це
     * той самий стан, тож CRC образу рахуємо по його справжній довжині. */
    uint8_t tail[PLAT_FLASH_WORD];
    const size_t whole = len - (len % PLAT_FLASH_WORD);

    if (!plat_flash_unlock()) {
        return false;
    }

    bool ok = true;
    if (whole > 0) {
        ok = bank_program_from_ram(addr, data, whole);
    }
    if (ok && whole < len) {
        memset(tail, 0xFF, sizeof(tail));
        memcpy(tail, data + whole, len - whole);
        ok = bank_program_from_ram(addr + whole, tail, sizeof(tail));
    }

    plat_flash_lock();
    return ok;
}

uint32_t flash_bank_crc(boot_bank_t bank, uint32_t len)
{
    if (len == 0 || len > BANK_SIZE) {
        return 0u;
    }
    const uint8_t *p = plat_flash_ptr(flash_bank_base(bank));
    if (p == NULL) {
        return 0u;
    }
    return crc32_update(0u, p, len);
}
