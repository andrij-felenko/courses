#include "tca9548a.h"

#include <stddef.h>

/* Даташит вимагає імпульсу ~RESET від 6 нс; 1 мкс — із величезним запасом. */
#define RESET_PULSE_US 1u

static io_status_t write_control(tca9548a_t *mux, uint8_t mask)
{
    io_status_t st = i2c_write(mux->addr, &mask, 1u);
    if (st == IO_OK) {
        mux->shadow = mask;
        mux->shadow_valid = true;
    } else {
        /* Невідомо, чи встиг комутатор засвоїти байт до зриву транзакції:
           тінь більше не дійсна, наступний виклик мусить писати наосліп. */
        mux->shadow_valid = false;
    }
    return st;
}

void tca9548a_hard_reset(tca9548a_t *mux)
{
    if (mux == NULL || mux->reset_pin == PIN_NONE) {
        return;
    }
    gpio_write(mux->reset_pin, false);
    delay_us(RESET_PULSE_US);
    gpio_write(mux->reset_pin, true);
    delay_us(RESET_PULSE_US);

    /* Після скидання регістр керування нульовий — усі ключі розімкнені. */
    mux->shadow = TCA9548A_ALL_OFF;
    mux->shadow_valid = true;
}

io_status_t tca9548a_init(tca9548a_t *mux, uint8_t addr, uint8_t reset_pin)
{
    if (mux == NULL) {
        return IO_ERR_ARG;
    }
    if (addr < TCA9548A_ADDR_BASE || addr > (uint8_t)(TCA9548A_ADDR_BASE + 7u)) {
        return IO_ERR_ARG;
    }

    mux->addr = addr;
    mux->reset_pin = reset_pin;
    mux->shadow = TCA9548A_ALL_OFF;
    mux->shadow_valid = false;

    /* Живлення могло й не зникати: теплий перезапуск МК лишає комутатор із
       відкритим каналом, а на ньому — чужий давач із такою самою адресою. */
    tca9548a_hard_reset(mux);
    return tca9548a_disable(mux);
}

io_status_t tca9548a_select(tca9548a_t *mux, uint8_t channel)
{
    uint8_t mask;
    io_status_t st;

    if (mux == NULL || channel >= TCA9548A_CHANNELS) {
        return IO_ERR_ARG;
    }
    mask = (uint8_t)(1u << channel);

    if (mux->shadow_valid && mux->shadow == mask) {
        return IO_OK;  /* канал уже відкритий — не палимо зайвих 45 мкс */
    }

    st = write_control(mux, mask);
    if (st != IO_OK && mux->reset_pin != PIN_NONE) {
        /* Комутатор міг зависнути з замкненими ключами й тримати ємність
           усіх субшин на головній лінії. Скидаємо апаратно й пробуємо ще. */
        tca9548a_hard_reset(mux);
        st = write_control(mux, mask);
    }
    return st;
}

io_status_t tca9548a_disable(tca9548a_t *mux)
{
    io_status_t st;

    if (mux == NULL) {
        return IO_ERR_ARG;
    }
    if (mux->shadow_valid && mux->shadow == TCA9548A_ALL_OFF) {
        return IO_OK;
    }

    st = write_control(mux, TCA9548A_ALL_OFF);
    if (st != IO_OK) {
        /* Лишити невідомо які ключі замкненими не можна: далі обмін піде з
           двома субшинами відразу. Апаратне скидання ізолює гарантовано,
           але помилку однаково віддаємо нагору — шина щойно збоїла. */
        tca9548a_hard_reset(mux);
    }
    return st;
}

io_status_t tca9548a_readback(const tca9548a_t *mux, uint8_t *mask)
{
    if (mux == NULL || mask == NULL) {
        return IO_ERR_ARG;
    }
    return i2c_read(mux->addr, mask, 1u);
}

io_status_t tca9548a_read_reg(tca9548a_t *mux, uint8_t channel, uint8_t dev,
                              uint8_t reg, uint8_t *buf, uint8_t len)
{
    io_status_t st;
    io_status_t off;

    if (mux == NULL || buf == NULL || len == 0u) {
        return IO_ERR_ARG;
    }

    st = tca9548a_select(mux, channel);
    if (st != IO_OK) {
        return st;
    }

    st = i2c_write_read(dev, &reg, 1u, buf, len);

    /* Субшину ізолюємо в будь-якому разі: ще одна транзакція на 45 мкс,
       зате наступний виклик не побачить ні чужої ємності, ні чужої адреси. */
    off = tca9548a_disable(mux);
    return (st != IO_OK) ? st : off;
}

io_status_t mux_bank_isolate(mux_bank_t *bank)
{
    io_status_t first = IO_OK;
    uint8_t i;

    if (bank == NULL || bank->mux == NULL || bank->count == 0u ||
        bank->count > TCA9548A_MAX_MUX) {
        return IO_ERR_ARG;
    }

    for (i = 0u; i < bank->count; ++i) {
        io_status_t st = tca9548a_disable(&bank->mux[i]);
        if (st != IO_OK && first == IO_OK) {
            first = st;  /* гасимо решту навіть після збою на одному чипі */
        }
    }
    return first;
}

io_status_t mux_bank_select(mux_bank_t *bank, uint8_t subbus)
{
    uint8_t index;
    uint8_t channel;
    uint8_t i;

    if (bank == NULL || bank->mux == NULL || bank->count == 0u ||
        bank->count > TCA9548A_MAX_MUX) {
        return IO_ERR_ARG;
    }

    index = (uint8_t)(subbus / TCA9548A_CHANNELS);
    channel = (uint8_t)(subbus % TCA9548A_CHANNELS);
    if (index >= bank->count) {
        return IO_ERR_ARG;
    }

    /* Спершу гасимо решту комутаторів. Два відкриті канали злили б дві
       субшини в одну — разом з їхніми однаковими адресами й ємністю. */
    for (i = 0u; i < bank->count; ++i) {
        io_status_t st;
        if (i == index) {
            continue;
        }
        st = tca9548a_disable(&bank->mux[i]);
        if (st != IO_OK) {
            return st;
        }
    }

    return tca9548a_select(&bank->mux[index], channel);
}

uint8_t mux_bank_poll(mux_bank_t *bank, uint8_t dev, uint8_t reg,
                      uint8_t *out, uint8_t len, uint64_t *fail_mask)
{
    uint64_t failed = 0u;
    uint8_t ok = 0u;
    uint8_t total;
    uint8_t sb;

    if (bank == NULL || bank->mux == NULL || out == NULL || len == 0u ||
        bank->count == 0u || bank->count > TCA9548A_MAX_MUX) {
        if (fail_mask != NULL) {
            *fail_mask = ~(uint64_t)0u;
        }
        return 0u;
    }

    total = (uint8_t)(bank->count * TCA9548A_CHANNELS);
    for (sb = 0u; sb < total; ++sb) {
        uint8_t *slot = &out[(size_t)sb * (size_t)len];

        if (mux_bank_select(bank, sb) != IO_OK ||
            i2c_write_read(dev, &reg, 1u, slot, len) != IO_OK) {
            /* Мертвий давач не зупиняє обхід: реєстратор мусить зібрати
               решту зон, а зламану лише позначити в масці невдач. */
            failed |= (uint64_t)1u << sb;
            continue;
        }
        ++ok;
    }

    (void)mux_bank_isolate(bank);
    if (fail_mask != NULL) {
        *fail_mask = failed;
    }
    return ok;
}
