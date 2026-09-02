/* Сама послідовність оживлення. Тут немає нічого про конкретний сенсор:
 * модуль перевіряє провідники, живлення й налаштування шини. */
#include "bringup.h"

#include <assert.h>
#include <stddef.h>

/* Шаховий патерн ловить містки між сусідніми розрядами, крайні маски —
 * залипання транзисторів у нуль і в одиницю. */
static const uint8_t PATTERNS[4] = { 0x55u, 0xAAu, 0x00u, 0xFFu };

static bool read_with_retry(const bus_driver_t *bus, const chip_config_t *cfg,
                            uint8_t reg, uint8_t *out, uint8_t *attempts)
{
    uint8_t n;

    for (n = 1u; n <= cfg->retries; ++n) {
        *attempts = n;
        if (bus->read_reg(bus->ctx, reg, out)) {
            return true;
        }
        /* Перехідні процеси живлення тривають довше, ніж один кадр: даємо
         * кристалу ще трохи часу, замість того щоб одразу здаватися. */
        bus->delay_ms(bus->ctx, cfg->retry_delay_ms);
    }
    return false;
}

/* Пара сусідніх розрядів, у які записали різні значення, а прочитали
 * однакові, — це або місток припою, або злиті тригери в кристалі. */
static uint8_t bridged_pairs(uint8_t written, uint8_t got)
{
    uint8_t mask = 0u;
    unsigned bit;

    for (bit = 0u; bit + 1u < 8u; ++bit) {
        unsigned w_lo = (written >> bit) & 1u;
        unsigned w_hi = (written >> (bit + 1u)) & 1u;
        unsigned g_lo = (got >> bit) & 1u;
        unsigned g_hi = (got >> (bit + 1u)) & 1u;

        if (w_lo != w_hi && g_lo == g_hi) {
            mask |= (uint8_t)(3u << bit);
        }
    }
    return mask;
}

/* Тест повнодуплексного тракту. Виконуємо всі чотири патерни, навіть коли
 * перший уже впав: масив несправних бітів набагато корисніший за перший
 * розбіжний байт, а вихідне значення регістра однаково треба відновити. */
static void run_scratchpad(const bus_driver_t *bus, const chip_config_t *cfg,
                           diagnostic_report_t *report)
{
    uint8_t original = 0u;
    uint8_t attempts = 0u;
    bool    failed = false;
    bool    every_readback_is_original = true;
    bool    some_pattern_differs = false;
    size_t  i;

    if (!read_with_retry(bus, cfg, cfg->scratchpad_reg, &original, &attempts)) {
        report->status = BRINGUP_NO_ANSWER;
        return;
    }

    for (i = 0u; i < sizeof PATTERNS; ++i) {
        uint8_t pattern = PATTERNS[i];
        uint8_t readback = 0u;

        if (!bus->write_reg(bus->ctx, cfg->scratchpad_reg, pattern) ||
            !bus->read_reg(bus->ctx, cfg->scratchpad_reg, &readback)) {
            (void)bus->write_reg(bus->ctx, cfg->scratchpad_reg, original);
            report->status = BRINGUP_NO_ANSWER;
            return;
        }

        if (pattern != original) {
            some_pattern_differs = true;
        }
        if (readback != original) {
            every_readback_is_original = false;
        }

        if (readback != pattern) {
            report->stuck_high |= (uint8_t)(~pattern & readback);
            report->stuck_low  |= (uint8_t)(pattern & ~readback);
            report->bridged    |= bridged_pairs(pattern, readback);

            if (!failed) {
                failed = true;
                report->written  = pattern;
                report->readback = readback;
            }
        }
    }

    /* Конфігураційний регістр лишаємо таким, яким його застали. */
    if (!bus->write_reg(bus->ctx, cfg->scratchpad_reg, original)) {
        report->status = BRINGUP_NO_ANSWER;
        return;
    }

    if (!failed) {
        report->scratchpad_done = true;
        report->status = BRINGUP_OK;
        return;
    }

    /* Якщо на кожен патерн повертається старе значення регістра, кристал
     * жодного нашого байта не бачив: обірвано лінію MOSI (або SDA у бік
     * чипа), а не спотворено окремі біти. */
    report->status = (every_readback_is_original && some_pattern_differs)
                         ? BRINGUP_WRITE_PATH_DEAD
                         : BRINGUP_SCRATCHPAD_BAD;
}

diagnostic_report_t bringup_validate(const bus_driver_t *bus, const chip_config_t *cfg)
{
    diagnostic_report_t report;
    uint8_t id = 0u;
    uint8_t i;

    /* Ідентифікатор із самих нулів або самих одиниць неможливо відрізнити
     * від мертвої шини — жоден виробник такого й не призначає. */
    assert(cfg->expected_id != 0x00u && cfg->expected_id != 0xFFu);
    assert(cfg->retries > 0u);

    for (i = 0u; i < (uint8_t)sizeof report; ++i) {
        ((uint8_t *)&report)[i] = 0u;
    }

    /* 1. Пауза t_POR: доки внутрішній детектор скидання не відпустить
     *    цифрове ядро, чип фізично не здатний декодувати команду. */
    bus->delay_ms(bus->ctx, cfg->t_por_ms);

    /* 2. WHO_AM_I з повторними спробами. */
    if (!read_with_retry(bus, cfg, cfg->id_reg, &id, &report.attempts)) {
        report.status = BRINGUP_NO_ANSWER;
        return report;
    }
    report.received_id = id;

    /* 3. Крайні байти — це не дані, а рівні напруги на лінії. */
    if (id == 0xFFu) {
        report.status = BRINGUP_BUS_STUCK_HIGH;
        return report;
    }
    if (id == 0x00u) {
        report.status = BRINGUP_BUS_STUCK_LOW;
        return report;
    }

    /* 4. Зсув рівно на один розряд: пайка ціла, помилка в конфігурації. */
    if (id == (uint8_t)(cfg->expected_id << 1)) {
        report.shift = BRINGUP_SHIFT_LEFT;
        report.status = BRINGUP_BIT_SHIFT;
        return report;
    }
    if (id == (uint8_t)(cfg->expected_id >> 1)) {
        report.shift = BRINGUP_SHIFT_RIGHT;
        report.status = BRINGUP_BIT_SHIFT;
        return report;
    }

    /* 5. Точна звірка з паспортом. */
    if (id != cfg->expected_id) {
        report.status = BRINGUP_FOREIGN_ID;
        return report;
    }

    /* 6. WHO_AM_I довів лише тракт читання — перевіряємо тракт запису. */
    run_scratchpad(bus, cfg, &report);
    return report;
}
