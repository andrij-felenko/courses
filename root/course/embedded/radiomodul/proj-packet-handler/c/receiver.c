#include "receiver.h"

#include <string.h>

#include "crc16.h"

enum { ST_HUNT = 0, ST_LEN, ST_DATA, ST_CRC };

static void back_to_hunt(receiver_t *rx)
{
    rx->state = ST_HUNT;
    rx->armed = false;
    rx->alt_run = 0;
    rx->bit_count = 0;
    rx->byte_acc = 0;
    rx->body_pos = 0;
    rx->crc_pos = 0;
}

void receiver_init(receiver_t *rx)
{
    memset(rx, 0, sizeof(*rx));
    back_to_hunt(rx);
}

static void fifo_push(receiver_t *rx, const uint8_t *data, uint8_t len)
{
    if (rx->count >= RX_FIFO_DEPTH) {
        /* Хост не встиг вичитати попередній кадр по SPI. Реальний трансивер
           тут піднімає ознаку переповнення й стоїть до CMD_FLUSHRX. */
        rx->overrun = true;
        rx->stats.overruns++;
        return;
    }

    packet_t *slot = &rx->fifo[(rx->head + rx->count) % RX_FIFO_DEPTH];
    memcpy(slot->data, data, len);
    slot->len = len;
    rx->count++;
}

bool receiver_pop(receiver_t *rx, packet_t *out)
{
    if (rx->count == 0) {
        return false;
    }
    *out = rx->fifo[rx->head];
    rx->head = (uint8_t)((rx->head + 1) % RX_FIFO_DEPTH);
    rx->count--;
    return true;
}

bool receiver_overrun(const receiver_t *rx)
{
    return rx->overrun;
}

void receiver_flush(receiver_t *rx)
{
    rx->head = 0;
    rx->count = 0;
    rx->overrun = false;
    back_to_hunt(rx);
}

/* Байт зібрано з восьми бітів — далі ним займається кадровий автомат. */
static void handle_byte(receiver_t *rx, uint8_t raw)
{
    /* Тіло кадру скрембльоване, і той самий LFSR знімає з нього маску. */
    const uint8_t byte = whitening_byte(&rx->w, raw);

    switch (rx->state) {
    case ST_LEN:
        if (byte == 0 || byte > PACKET_MAX_PAYLOAD) {
            /* Найчастіша причина — фантомне спрацювання корелятора в шумі:
               синхрослово «знайшлось», а за ним нема жодного кадру. */
            rx->stats.len_errs++;
            back_to_hunt(rx);
            return;
        }
        rx->need = byte;
        rx->crc = crc16_update(rx->crc, byte);
        rx->state = ST_DATA;
        return;

    case ST_DATA:
        rx->body[rx->body_pos++] = byte;
        rx->crc = crc16_update(rx->crc, byte);
        if (rx->body_pos == rx->need) {
            rx->state = ST_CRC;
        }
        return;

    case ST_CRC:
        rx->crc_rx[rx->crc_pos++] = byte;
        if (rx->crc_pos < 2) {
            return;
        }
        {
            const uint16_t received =
                (uint16_t)(((uint16_t)rx->crc_rx[0] << 8) | rx->crc_rx[1]);

            if (received == rx->crc) {
                rx->stats.good++;
                fifo_push(rx, rx->body, rx->need);
            } else {
                /* Апаратний блок у цьому місці просто не піднімає RX_DONE
                   і скидає покажчик FIFO — кадр зникає мовчки. */
                rx->stats.crc_errs++;
            }
        }
        back_to_hunt(rx);
        return;

    case ST_HUNT:
    default:
        back_to_hunt(rx);
        return;
    }
}

void receiver_push_bit(receiver_t *rx, uint8_t bit_in)
{
    const uint8_t bit = (uint8_t)(bit_in & 1u);

    if (rx->state == ST_HUNT) {
        /* Детектор преамбули: рахуємо довжину серії чергувань 0/1.
           Поки серії не було, корелятор вимкнено — інакше тепловий шум
           сам ловив би синхрослово кілька разів на секунду. */
        rx->alt_run = (bit != rx->last_bit) ? (uint16_t)(rx->alt_run + 1u) : 1u;
        rx->last_bit = bit;

        if (!rx->armed && rx->alt_run >= PREAMBLE_DETECT_BITS) {
            rx->armed = true;
            rx->search_left = SYNC_SEARCH_BITS;
            rx->stats.arms++;
        }

        rx->shift = (rx->shift << 1) | bit;

        if (!rx->armed) {
            return;
        }

        if ((rx->shift & SYNC_MASK) == SYNC_WORD) {
            /* Строб байтового вирівнювання: наступний біт стає старшим бітом
               першого байта тіла кадру. Саме тут з потоку бітів народжуються
               байти — жодної іншої межі в ефірі немає. */
            rx->stats.syncs++;
            rx->state = ST_LEN;
            rx->bit_count = 0;
            rx->byte_acc = 0;
            rx->body_pos = 0;
            rx->crc_pos = 0;
            whitening_init(&rx->w);
            rx->crc = CRC16_INIT;
            return;
        }

        if (--rx->search_left == 0) {
            /* Вікно вийшло: то була не преамбула, а щось на неї схоже. */
            rx->armed = false;
            rx->alt_run = 0;
        }
        return;
    }

    /* Усередині кадру просто збираємо байти, старший біт першим. */
    rx->byte_acc = (uint8_t)((rx->byte_acc << 1) | bit);
    if (++rx->bit_count == 8) {
        const uint8_t raw = rx->byte_acc;
        rx->bit_count = 0;
        rx->byte_acc = 0;
        handle_byte(rx, raw);
    }
}

void receiver_push_byte_msb(receiver_t *rx, uint8_t byte)
{
    for (int bit = 7; bit >= 0; bit--) {
        receiver_push_bit(rx, (uint8_t)((byte >> bit) & 1u));
    }
}
