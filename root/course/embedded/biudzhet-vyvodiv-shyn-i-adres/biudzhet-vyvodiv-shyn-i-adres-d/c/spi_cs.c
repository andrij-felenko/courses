#include "spi_cs.h"

#include <stddef.h>

void cs_decoder_init(cs_decoder_t *d, uint8_t a0, uint8_t a1, uint8_t a2,
                     uint8_t a3, uint8_t en)
{
    if (d == NULL) {
        return;
    }

    d->pin_a0 = a0;
    d->pin_a1 = a1;
    d->pin_a2 = a2;
    d->pin_a3 = a3;
    d->pin_en = en;
    d->lines = (a3 == PIN_NONE) ? 8u : 16u;
    d->active = CS_NONE;

    /* Найперша дія на старті — зняти дозвіл. Поки строб не піднято, а
       адресні лінії ще у своєму скиданому стані, дешифратор тримає якийсь
       випадковий Yn у нулі, і чип уже слухає шину, якої ще не налаштовано. */
    gpio_write(en, true);
    gpio_write(a0, false);
    gpio_write(a1, false);
    gpio_write(a2, false);
    if (a3 != PIN_NONE) {
        gpio_write(a3, false);
    }
}

io_status_t cs_select(cs_decoder_t *d, uint8_t device)
{
    if (d == NULL) {
        return IO_ERR_ARG;
    }
    if (device >= d->lines) {
        return IO_ERR_ARG;
    }

    /* 1. Знімаємо дозвіл: усі виходи Y підіймаються в 1, жодного чипа не
          вибрано. Саме це вбиває гліч — далі адресу можна міняти вільно. */
    gpio_write(d->pin_en, true);

    /* 2. Виставляємо двійковий номер пристрою. Різний час перемикання
          виводів МК тепер не важить: виходи дешифратора заблоковані. */
    gpio_write(d->pin_a0, (device & 0x01u) != 0u);
    gpio_write(d->pin_a1, (device & 0x02u) != 0u);
    gpio_write(d->pin_a2, (device & 0x04u) != 0u);
    if (d->pin_a3 != PIN_NONE) {
        /* Старший біт вибирає, який із двох каскадованих чипів дозволено. */
        gpio_write(d->pin_a3, (device & 0x08u) != 0u);
    }

    /* 3. Даємо дозвіл: рівно один вихід падає в нуль через 15..20 нс.
          Окремої затримки не треба — запис у регістр SPI і так довший. */
    gpio_write(d->pin_en, false);
    d->active = device;
    return IO_OK;
}

void cs_release(cs_decoder_t *d)
{
    if (d == NULL) {
        return;
    }
    gpio_write(d->pin_en, true);
    d->active = CS_NONE;
}

io_status_t spi_cs_command(cs_decoder_t *d, uint8_t device,
                           const uint8_t *cmd, uint16_t cmd_len,
                           const uint8_t *tx, uint8_t *rx, uint16_t len)
{
    io_status_t st;

    if (d == NULL) {
        return IO_ERR_ARG;
    }
    if ((cmd_len != 0u && cmd == NULL) ||
        (len != 0u && tx == NULL && rx == NULL)) {
        return IO_ERR_ARG;
    }

    st = cs_select(d, device);
    if (st != IO_OK) {
        return st;
    }

    if (cmd_len != 0u) {
        st = spi_transfer(cmd, NULL, cmd_len);
        if (st != IO_OK) {
            goto out;
        }
    }
    if (len != 0u) {
        st = spi_transfer(tx, rx, len);
    }

out:
    /* Єдиний вихід із функції. Лінія CS мусить піднятися і на помилці:
       інакше ведений лишиться посеред недочитаної транзакції й зіпсує
       наступну — а на спільному дешифраторі це помітять усі вісім чипів. */
    cs_release(d);
    return st;
}
