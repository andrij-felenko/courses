#include <stdio.h>
#include <string.h>

#include "packet.h"
#include "receiver.h"

/* Дешевий xorshift замість rand(): зерно фіксоване, тож «ефірний шум»
   при кожному запуску той самий і числа в кінці відтворювані. */
static uint32_t g_rng = 0x2DD4A55Au;

static uint8_t noise_bit(void)
{
    g_rng ^= g_rng << 13;
    g_rng ^= g_rng >> 17;
    g_rng ^= g_rng << 5;
    return (uint8_t)(g_rng & 1u);
}

static void hexdump(const char *tag, const uint8_t *data, size_t len)
{
    printf("%s (%zu Б):", tag, len);
    for (size_t i = 0; i < len; i++) {
        printf(" %02X", data[i]);
    }
    putchar('\n');
}

/* Ефір: спершу трохи шуму, далі кадр біт за бітом, старшим уперед. */
static void air_send(receiver_t *rx, const uint8_t *frame, size_t len,
                     unsigned noise_bits)
{
    for (unsigned i = 0; i < noise_bits; i++) {
        receiver_push_bit(rx, noise_bit());
    }
    for (size_t i = 0; i < len; i++) {
        receiver_push_byte_msb(rx, frame[i]);
    }
}

/* Та сама передача, але з переставленим порядком бітів у байті. */
static void air_send_lsb_first(receiver_t *rx, const uint8_t *frame, size_t len)
{
    for (size_t i = 0; i < len; i++) {
        for (int bit = 0; bit < 8; bit++) {
            receiver_push_bit(rx, (uint8_t)((frame[i] >> bit) & 1u));
        }
    }
}

int main(void)
{
    static const uint8_t payload[] = "TELEMETRY:BAT=3.81V";
    const uint8_t payload_len = (uint8_t)(sizeof(payload) - 1u);

    uint8_t frame[PACKET_MAX_FRAME];
    const size_t frame_len = packet_build(payload, payload_len, frame, sizeof(frame));
    if (frame_len == 0) {
        fprintf(stderr, "кадр не зібрано\n");
        return 1;
    }
    hexdump("кадр в ефір", frame, frame_len);

    receiver_t rx;
    receiver_init(&rx);
    packet_t got;

    /* 1. Нормальний прийом. Перед кадром 13 бітів шуму — число навмисно
          не кратне восьми: вирівнювання дає корелятор, а не межа байта. */
    air_send(&rx, frame, frame_len, 13);
    if (receiver_pop(&rx, &got)) {
        printf("1) прийнято %u Б: %.*s\n", got.len, (int)got.len, (const char *)got.data);
    } else {
        printf("1) кадр не прийнято\n");
    }

    /* 2. Один перевернутий біт у тілі кадру — CRC не сходиться. */
    uint8_t broken[PACKET_MAX_FRAME];
    memcpy(broken, frame, frame_len);
    broken[PREAMBLE_LEN + 2 + 3] ^= 0x08u;
    air_send(&rx, broken, frame_len, 7);
    {
        const bool delivered = receiver_pop(&rx, &got);
        printf("2) помилок CRC: %u, кадр у FIFO: %s\n",
               rx.stats.crc_errs, delivered ? "є" : "немає");
    }

    /* 3. FIFO глибиною два: шлемо три кадри поспіль і не вичитуємо жодного. */
    receiver_flush(&rx);
    for (int i = 0; i < 3; i++) {
        air_send(&rx, frame, frame_len, 5);
    }
    printf("3) переповнення FIFO: %s, втрачено кадрів: %u\n",
           receiver_overrun(&rx) ? "так" : "ні", rx.stats.overruns);
    receiver_flush(&rx); /* CMD_FLUSHRX — без нього приймач так і стоятиме */

    /* 4. Той самий кадр, але біти в байті йдуть молодшим першим:
          візерунок синхрослова розсипається, корелятор мовчить. */
    {
        const uint32_t syncs_before = rx.stats.syncs;
        air_send_lsb_first(&rx, frame, frame_len);
        printf("4) LSB first: спрацювань корелятора %u\n",
               rx.stats.syncs - syncs_before);
    }

    /* 5. Порожній ефір: 2 млн бітів шуму — це близько 8 с на 250 кбіт/с.
          Детектор преамбули зводиться десятки разів, але корелятор за
          свої короткі вікна майже ніколи не знаходить синхрослова. */
    receiver_init(&rx);
    for (unsigned long i = 0; i < 2000000ul; i++) {
        receiver_push_bit(&rx, noise_bit());
    }
    printf("5) шум: преамбул %u, синхрослів %u, брак довжини %u, кадрів %u\n",
           rx.stats.arms, rx.stats.syncs, rx.stats.len_errs, rx.stats.good);

    return 0;
}
