/* opus_demo.c - Використання libopus API мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <opus/opus.h>

#define SAMPLE_RATE 48000
#define CHANNELS 1
#define FRAME_SIZE 960 /* 20 мс при 48 кГц */
#define MAX_PACKET_SIZE 1500

int main(void) {
    int error = OPUS_OK;

    /* 1. Створення та ініціалізація кодера */
    OpusEncoder *encoder = opus_encoder_create(SAMPLE_RATE, CHANNELS, OPUS_APPLICATION_VOIP, &error);
    if (error != OPUS_OK) {
        fprintf(stderr, "Помилка створення кодера: %s\n", opus_strerror(error));
        return EXIT_FAILURE;
    }

    /* 2. Налаштування параметрів кодера через control-виклики */
    opus_encoder_ctl(encoder, OPUS_SET_BITRATE(24000));          /* 24 кбіт/с */
    opus_encoder_ctl(encoder, OPUS_SET_VBR(1));                  /* Змінний бітрейт VBR */
    opus_encoder_ctl(encoder, OPUS_SET_COMPLEXITY(8));           /* Обчислювальна складність 0-10 */
    opus_encoder_ctl(encoder, OPUS_SET_INBAND_FEC(1));           /* Ввімкнути In-Band FEC */
    opus_encoder_ctl(encoder, OPUS_SET_PACKET_LOSS_PERC(10));    /* Очікувані втрати 10% */

    /* 3. Створення декодера */
    OpusDecoder *decoder = opus_decoder_create(SAMPLE_RATE, CHANNELS, &error);
    if (error != OPUS_OK) {
        fprintf(stderr, "Помилка створення декодера: %s\n", opus_strerror(error));
        opus_encoder_destroy(encoder);
        return EXIT_FAILURE;
    }

    /* Буфери для PCM та стиснутих даних */
    int16_t pcm_in[FRAME_SIZE] = {0};
    uint8_t opus_packet[MAX_PACKET_SIZE];
    int16_t pcm_out[FRAME_SIZE];

    /* 4. Кодування кадру PCM -> Opus */
    opus_int32 bytes_encoded = opus_encode(encoder, pcm_in, FRAME_SIZE, opus_packet, MAX_PACKET_SIZE);
    if (bytes_encoded < 0) {
        fprintf(stderr, "Помилка кодування: %s\n", opus_strerror(bytes_encoded));
    } else {
        printf("Успішно закодовано %d відліків у пакет розміром %d байт\n", FRAME_SIZE, bytes_encoded);
    }

    /* 5. Декодування кадру Opus -> PCM */
    int samples_decoded = opus_decode(decoder, opus_packet, bytes_encoded, pcm_out, FRAME_SIZE, 0);
    if (samples_decoded < 0) {
        fprintf(stderr, "Помилка декодування: %s\n", opus_strerror(samples_decoded));
    } else {
        printf("Успішно декодовано %d відліків PCM\n", samples_decoded);
    }

    /* 6. Звільнення ресурсів */
    opus_encoder_destroy(encoder);
    opus_decoder_destroy(decoder);

    return EXIT_SUCCESS;
}
