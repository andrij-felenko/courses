#include <stdbool.h>
#include <stdint.h>

#include "boot_state.h"
#include "efuse.h"
#include "manifest.h"
#include "verify.h"

/* ------------------------------------------------------------------ *
 *  Карта Flash і мінімальна периферія завантажувача
 * ------------------------------------------------------------------ */

#define SLOT_A_BASE   0x08010000UL
#define SLOT_B_BASE   0x08090000UL
#define SLOT_SIZE     0x00080000UL

#define SRAM_BASE     0x20000000UL
#define SRAM_SIZE     0x00020000UL

typedef struct {
    volatile uint32_t SR;
    volatile uint32_t DR;
} uart_regs_t;

#define UART          ((uart_regs_t *)0x40013800UL)
#define UART_SR_TXE   (1U << 7)

#define IWDG_KR       (*(volatile uint32_t *)0x40003000UL)
#define IWDG_RELOAD   0x0000AAAAUL

#define SCB_VTOR      (*(volatile uint32_t *)0xE000ED08UL)

static void log_str(const char *text)
{
    while (*text != '\0') {
        while ((UART->SR & UART_SR_TXE) == 0U) {
            /* чекаємо, поки звільниться регістр передавання */
        }
        UART->DR = (uint32_t)(uint8_t)*text++;
    }
}

static void log_event(const char *prefix, boot_status_t status)
{
    log_str(prefix);
    log_str(": ");
    log_str(boot_status_str(status));
    log_str("\r\n");
}

static const uint8_t *slot_base(boot_slot_t slot)
{
    return (const uint8_t *)((slot == BOOT_SLOT_B) ? SLOT_B_BASE : SLOT_A_BASE);
}

/* ------------------------------------------------------------------ *
 *  Перевірка банку
 * ------------------------------------------------------------------ */

static boot_status_t load_and_verify(boot_slot_t slot,
                                     const efuse_mirror_t *efuse,
                                     firmware_manifest_t *manifest)
{
    const uint8_t *base = slot_base(slot);

    boot_status_t status = manifest_parse(base, SLOT_SIZE, manifest);
    if (status != BOOT_OK) {
        return status;
    }

    /* Образ мусить стартувати всередині свого ж банку, а не де завгодно. */
    if (manifest->load_address < (uint32_t)(uintptr_t)base ||
        manifest->load_address >= (uint32_t)(uintptr_t)base + SLOT_SIZE) {
        return BOOT_ERR_FLASH_READ;
    }

    return boot_verify_image(manifest, manifest_payload(base), efuse);
}

/*
 * Готуємо, але НЕ виконуємо ротацію. Якщо новий образ підписано старшим слотом,
 * усі молодші слоти підлягають відкликанню — але спалимо ми їх аж тоді, коли
 * застосунок доповість про працездатність. До того моменту старий банк лишається
 * робочим шляхом назад.
 */
static void plan_rotation(boot_state_t *state,
                          const firmware_manifest_t *manifest,
                          const efuse_mirror_t *efuse)
{
    uint32_t mask = 0U;
    for (uint8_t slot = 0; slot < manifest->key_slot_index; ++slot) {
        if ((efuse->revocation_bits & (1U << slot)) == 0U) {
            mask |= (1U << slot);
        }
    }
    state->pending_revoke_mask = mask;

    if (manifest->security_version > efuse->monotonic_counter &&
        manifest->security_version <= EFUSE_COUNTER_BITS) {
        state->pending_counter = manifest->security_version;
    } else {
        /*
         * Або версія не зросла, або термометр вичерпано. Друге — не аварія
         * завантаження: образ чинний, просто далі піднімати лічильник нікуди,
         * і про це має дізнатись виробництво.
         */
        state->pending_counter = 0U;
        if (manifest->security_version > EFUSE_COUNTER_BITS) {
            log_str("efuse: anti-rollback counter exhausted\r\n");
        }
    }
}

/* ------------------------------------------------------------------ *
 *  Запуск і аварійний режим
 * ------------------------------------------------------------------ */

static void jump_to_application(uint32_t load_address)
{
    const uint32_t *vectors = (const uint32_t *)(uintptr_t)load_address;
    const uint32_t stack_pointer = vectors[0];
    const uint32_t reset_handler = vectors[1];

    /* Вектор скидання й вершина стека мусять вказувати в дозволені області. */
    if (stack_pointer < SRAM_BASE || stack_pointer > SRAM_BASE + SRAM_SIZE ||
        reset_handler < load_address) {
        log_event("jump", BOOT_ERR_FLASH_READ);
        for (;;) {
            IWDG_KR = IWDG_RELOAD;
        }
    }

    log_str("boot: jumping to application\r\n");

    __asm volatile("cpsid i");
    SCB_VTOR = load_address;
    __asm volatile("msr msp, %0" : : "r"(stack_pointer) : "memory");
    __asm volatile("dsb; isb");

    ((void (*)(void))reset_handler)();

    for (;;) {
        /* сюди не повертаються */
    }
}

/*
 * Жодного чинного образу немає. Це НЕ привід стирати банки чи палити перемички:
 * лишаємось у завантажувачі, годуємо сторожовий таймер і чекаємо оновлення
 * по службовому інтерфейсу. Пристрій живий, хай і без застосунку.
 */
static void enter_recovery(boot_status_t reason)
{
    log_event("recovery", reason);

    for (;;) {
        IWDG_KR = IWDG_RELOAD;
    }
}

/* ------------------------------------------------------------------ *
 *  Точка входу
 * ------------------------------------------------------------------ */

int main(void)
{
    verify_init();
    log_str("\r\nbootloader stage 2\r\n");

    efuse_mirror_t efuse;
    boot_status_t status = efuse_read_mirror(&efuse);
    if (status != BOOT_OK) {
        /* Без кореня довіри перевіряти образ немає чим. */
        enter_recovery(status);
    }

    boot_state_t state;
    boot_state_load(&state);

    /* Пробний образ вичерпав спроби — примусовий відкіт на попередній банк. */
    if (state.status == STATUS_TESTING && state.try_count >= BOOT_MAX_TRIES) {
        log_str("boot: test image failed to confirm, rolling back\r\n");
        state.active_slot = state.previous_slot;
        state.status = STATUS_CONFIRMED;
        state.try_count = 0U;
        state.pending_revoke_mask = 0U;
        state.pending_counter = 0U;
        (void)boot_state_store(&state);
    }

    boot_slot_t candidate = (boot_slot_t)state.active_slot;
    firmware_manifest_t manifest;

    status = load_and_verify(candidate, &efuse, &manifest);
    if (status != BOOT_OK) {
        log_event("verify", status);

        /*
         * Активний банк не проходить перевірку. Якщо він був пробним, у нас
         * лишається підтверджений попередник — саме заради цієї гілки ми й
         * не палили перемички наперед.
         */
        if ((uint32_t)candidate != state.previous_slot) {
            candidate = (boot_slot_t)state.previous_slot;
            status = load_and_verify(candidate, &efuse, &manifest);
            if (status == BOOT_OK) {
                log_str("boot: fell back to previous bank\r\n");
                state.active_slot = (uint32_t)candidate;
                state.status = STATUS_CONFIRMED;
                state.try_count = 0U;
                state.pending_revoke_mask = 0U;
                state.pending_counter = 0U;
                (void)boot_state_store(&state);
            } else {
                log_event("verify(previous)", status);
            }
        }
    }

    if (status != BOOT_OK) {
        enter_recovery(status);
    }

    if (state.status == STATUS_TESTING) {
        state.try_count += 1U;
        plan_rotation(&state, &manifest, &efuse);

        /*
         * Лічильник спроб пишемо ДО стрибка. Інакше застосунок, що падає
         * у HardFault до підтвердження, крутив би нескінченний цикл скидів:
         * try_count ніколи б не доріс до стелі, і відкат не настав би.
         */
        boot_status_t write_status = boot_state_store(&state);
        if (write_status != BOOT_OK) {
            enter_recovery(write_status);
        }
        log_str("boot: test run of staged image\r\n");
    }

    jump_to_application(manifest.load_address);
    return 0;
}
