#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#include "boot_state.h"
#include "crc32.h"
#include "efuse.h"

/* ------------------------------------------------------------------ *
 *  Мінімальний драйвер Flash: одна сторінка під запис стану.
 * ------------------------------------------------------------------ */

typedef struct {
    volatile uint32_t ACR;
    volatile uint32_t KEYR;
    volatile uint32_t OPTKEYR;
    volatile uint32_t SR;
    volatile uint32_t CR;
    volatile uint32_t AR;
} flash_regs_t;

#define FLASHC             ((flash_regs_t *)0x40022000UL)
#define FLASH_KEY1         0x45670123UL
#define FLASH_KEY2         0xCDEF89ABUL

#define FLASH_CR_PG        (1U << 0)
#define FLASH_CR_PER       (1U << 1)
#define FLASH_CR_STRT      (1U << 6)
#define FLASH_CR_LOCK      (1U << 7)

#define FLASH_SR_BSY       (1U << 0)
#define FLASH_SR_PGERR     (1U << 2)
#define FLASH_SR_WRPRTERR  (1U << 4)
#define FLASH_SR_EOP       (1U << 5)

#define BOOT_STATE_PAGE    0x0800F800UL  /* остання сторінка області завантажувача */
#define FLASH_TIMEOUT      400000U

static boot_status_t flash_wait(void)
{
    for (uint32_t spins = 0; spins < FLASH_TIMEOUT; ++spins) {
        if ((FLASHC->SR & FLASH_SR_BSY) == 0U) {
            if ((FLASHC->SR & (FLASH_SR_PGERR | FLASH_SR_WRPRTERR)) != 0U) {
                FLASHC->SR = FLASH_SR_PGERR | FLASH_SR_WRPRTERR | FLASH_SR_EOP;
                return BOOT_ERR_STATE_WRITE;
            }
            FLASHC->SR = FLASH_SR_EOP;
            return BOOT_OK;
        }
    }
    return BOOT_ERR_STATE_WRITE;
}

static void flash_unlock(void)
{
    if ((FLASHC->CR & FLASH_CR_LOCK) != 0U) {
        FLASHC->KEYR = FLASH_KEY1;
        FLASHC->KEYR = FLASH_KEY2;
    }
}

static void flash_lock(void)
{
    FLASHC->CR |= FLASH_CR_LOCK;
}

static boot_status_t flash_erase_state_page(void)
{
    boot_status_t rc = flash_wait();
    if (rc != BOOT_OK) {
        return rc;
    }

    FLASHC->CR |= FLASH_CR_PER;
    FLASHC->AR = BOOT_STATE_PAGE;
    FLASHC->CR |= FLASH_CR_STRT;

    rc = flash_wait();
    FLASHC->CR &= ~(uint32_t)(FLASH_CR_PER | FLASH_CR_STRT);
    return rc;
}

/* Контролер програмує півсловами, тож і пишемо півсловами. */
static boot_status_t flash_write_state_page(const void *source, size_t length)
{
    const uint16_t *words = (const uint16_t *)source;
    volatile uint16_t *target = (volatile uint16_t *)BOOT_STATE_PAGE;

    FLASHC->CR |= FLASH_CR_PG;

    boot_status_t rc = BOOT_OK;
    for (size_t i = 0; i < length / 2U; ++i) {
        target[i] = words[i];
        rc = flash_wait();
        if (rc != BOOT_OK) {
            break;
        }
    }

    FLASHC->CR &= ~(uint32_t)FLASH_CR_PG;
    return rc;
}

/* ------------------------------------------------------------------ *
 *  Запис стану
 * ------------------------------------------------------------------ */

static uint32_t state_crc(const boot_state_t *state)
{
    const uint8_t *bytes = (const uint8_t *)state;
    return crc32_ieee(bytes + 8, sizeof(*state) - 8U);
}

void boot_state_load(boot_state_t *state)
{
    memcpy(state, (const void *)BOOT_STATE_PAGE, sizeof(*state));

    const bool intact = (state->magic == BOOT_STATE_MAGIC) &&
                        (state->crc == state_crc(state)) &&
                        (state->active_slot <= BOOT_SLOT_B) &&
                        (state->previous_slot <= BOOT_SLOT_B) &&
                        (state->status == STATUS_CONFIRMED || state->status == STATUS_TESTING);

    if (intact) {
        return;
    }

    /*
     * Сторінка чиста або зіпсована обривом живлення. Безпечний дефолт —
     * банк A у підтвердженому стані: він або справді підтверджений, або
     * не пройде верифікацію й нас винесе в аварійний режим.
     */
    memset(state, 0, sizeof(*state));
    state->magic = BOOT_STATE_MAGIC;
    state->active_slot = BOOT_SLOT_A;
    state->previous_slot = BOOT_SLOT_A;
    state->status = STATUS_CONFIRMED;
}

boot_status_t boot_state_store(boot_state_t *state)
{
    state->magic = BOOT_STATE_MAGIC;
    state->crc = state_crc(state);

    flash_unlock();

    boot_status_t rc = flash_erase_state_page();
    if (rc == BOOT_OK) {
        rc = flash_write_state_page(state, sizeof(*state));
    }

    flash_lock();

    if (rc != BOOT_OK) {
        return rc;
    }

    /* Контрольне перечитування: запис у Flash мусить бути видимим одразу. */
    boot_state_t written;
    memcpy(&written, (const void *)BOOT_STATE_PAGE, sizeof(written));
    if (memcmp(&written, state, sizeof(written)) != 0) {
        return BOOT_ERR_STATE_WRITE;
    }

    return BOOT_OK;
}

boot_status_t boot_stage_update(boot_slot_t new_slot)
{
    boot_state_t state;
    boot_state_load(&state);

    if (state.status == STATUS_TESTING) {
        /*
         * Пробний запуск ще не підтверджено — нове оновлення поверх нього
         * стерло б єдиний відомий шлях назад.
         */
        return BOOT_ERR_NOT_TESTING;
    }

    state.previous_slot = state.active_slot;
    state.active_slot = (uint32_t)new_slot;
    state.status = STATUS_TESTING;
    state.try_count = 0U;
    state.pending_revoke_mask = 0U;
    state.pending_counter = 0U;

    return boot_state_store(&state);
}

boot_status_t boot_confirm_update(void)
{
    boot_state_t state;
    boot_state_load(&state);

    if (state.status != STATUS_TESTING) {
        /* Підтверджувати нічого: ми не в пробному запуску. */
        return BOOT_ERR_NOT_TESTING;
    }

    /*
     * Порядок операцій тут — не смак, а вимога. Спершу палимо перемички
     * (незворотна частина), і лише коли ЗАЛІЗО підтвердило кожен біт,
     * переводимо запис у CONFIRMED. Зворотний порядок дав би стан, у якому
     * стан каже «підтверджено», а ключі досі чинні.
     */
    for (uint8_t slot = 0; slot < BOOT_KEY_SLOTS; ++slot) {
        if ((state.pending_revoke_mask & (1U << slot)) == 0U) {
            continue;
        }
        boot_status_t rc = efuse_burn_revocation(slot);
        if (rc != BOOT_OK) {
            /*
             * Перемичка не спалилась (просіла напруга, комірка метастабільна).
             * Лишаємось у STATUS_TESTING: застосунок повторить підтвердження
             * пізніше, а завантажувач досі вміє відкотитись на старий банк.
             */
            return rc;
        }
    }

    if (state.pending_counter != 0U) {
        boot_status_t rc = efuse_burn_counter(state.pending_counter);
        if (rc != BOOT_OK) {
            return rc;
        }
    }

    state.status = STATUS_CONFIRMED;
    state.previous_slot = state.active_slot;
    state.try_count = 0U;
    state.pending_revoke_mask = 0U;
    state.pending_counter = 0U;

    return boot_state_store(&state);
}
