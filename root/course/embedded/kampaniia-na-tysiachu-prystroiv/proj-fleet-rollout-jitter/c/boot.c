#include "boot.h"

#include "platform.h"

#include <stdio.h>

static bool bank_intact(const ota_state_t *st, boot_bank_t bank)
{
    const uint32_t len = st->bank_len[bank];
    if (len == 0u) {
        return false;   /* банк порожній або ніколи не реєструвався */
    }
    return flash_bank_crc(bank, len) == st->bank_crc[bank];
}

boot_decision_t boot_select(void)
{
    ota_state_t st;
    ota_state_load(&st);

    boot_decision_t d = { BOOT_RUN, st.active_bank, 0u, st.boot_failures };
    bool rolled_back = false;
    bool dirty = false;

    /* Прапорець ще стоїть — отже, попередній старт нового образу не дійшов до
     * підтвердження: або паніка ядра, або сторожовий таймер, або зникло
     * живлення. Лічильник живе в незалежній пам'яті, тому переживає все це. */
    if (st.trial_pending) {
        if (st.boot_failures < 0xFFu) {
            st.boot_failures++;
        }
        dirty = true;

        if (st.boot_failures >= MAX_ALLOWED_CRASHES) {
            st.active_bank   = flash_other_bank(st.active_bank);
            st.trial_pending = false;
            st.boot_failures = 0;
            rolled_back = true;
        }
        d.failures = st.boot_failures;
    }

    /* Цілісність вибраного банку перевіряємо в будь-якому разі: образ міг
     * постраждати від обірваного запису або зношеного сектора. */
    if (!bank_intact(&st, st.active_bank)) {
        const boot_bank_t fallback = flash_other_bank(st.active_bank);
        if (bank_intact(&st, fallback)) {
            st.active_bank   = fallback;
            st.trial_pending = false;
            st.boot_failures = 0;
            rolled_back = true;
            dirty = true;
        } else {
            if (dirty) {
                ota_state_store(&st);
            }
            d.kind = BOOT_NO_IMAGE;
            d.bank = st.active_bank;
            d.entry = 0u;
            return d;
        }
    }

    if (dirty) {
        ota_state_store(&st);
    }

    d.kind  = rolled_back ? BOOT_ROLLED_BACK : BOOT_RUN;
    d.bank  = st.active_bank;
    d.entry = flash_bank_base(st.active_bank);
    return d;
}

#if defined(__arm__)

/* Адреси регістрів ядра Cortex-M — з архітектурного довідника, без сторонніх
 * заголовків: завантажувач збирається окремо й нічого зайвого не тягне. */
#define SCB_VTOR (*(volatile uint32_t *)0xE000ED08u)

void boot_jump(uint32_t bank_base)
{
    const uint32_t *vectors = (const uint32_t *)bank_base;
    const uint32_t stack_top = vectors[0];
    const uint32_t reset_handler = vectors[1];

    __asm volatile ("cpsid i" ::: "memory");   /* переривання ще від старого образу */
    SCB_VTOR = bank_base;
    __asm volatile ("dsb; isb" ::: "memory");
    __asm volatile ("msr msp, %0" :: "r" (stack_top) : );
    __asm volatile ("bx %0" :: "r" (reset_handler));

    for (;;) { }
}

#else

void boot_jump(uint32_t bank_base)
{
    /* На хості стрибка немає: далі main.c просто викликає застосунок. */
    printf("[boot] VTOR = 0x%08X, передаємо керування\n", (unsigned)bank_base);
}

#endif
