/* c_nfc_relay_verifier.c - C implementation of NFC RTT Timing Verifier */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <nfc/nfc.h>

#define MAX_ALLOWED_RTT_US 15000L  /* Гранична затримка: 15 мс (15 000 мкс) */
#define BUFFER_SIZE 264

typedef struct {
    uint8_t data[BUFFER_SIZE];
    size_t length;
    int64_t rtt_microseconds;
} nfc_apdu_response_t;

/* Отримання поточного монотонного часу в мікросекундах */
static int64_t get_monotonic_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ((int64_t)ts.tv_sec * 1000000L) + (ts.tv_nsec / 1000L);
}

/* Надсилання APDU-команди з точним вимірюванням RTT */
bool nfc_send_apdu_with_timing(nfc_device *pnd, 
                               const uint8_t *apdu_tx, 
                               size_t tx_len, 
                               nfc_apdu_response_t *resp) {
    if (!pnd || !apdu_tx || !resp || tx_len == 0) {
        return false;
    }

    int64_t start_time = get_monotonic_time_us();

    /* Виклик трансферу кадрів libnfc */
    int res = nfc_initiator_transceive_bytes(pnd, apdu_tx, tx_len, 
                                             resp->data, BUFFER_SIZE, -1);
    int64_t end_time = get_monotonic_time_us();

    if (res < 0) {
        fprintf(stderr, "Помилка передачі APDU кадру: %d\n", res);
        return false;
    }

    resp->length = (size_t)res;
    resp->rtt_microseconds = end_time - start_time;
    return true;
}

int main(void) {
    nfc_context *context = NULL;
    nfc_device *pnd = NULL;

    nfc_init(&context);
    if (!context) {
        fprintf(stderr, "Не вдалося ініціалізувати libnfc context\n");
        return EXIT_FAILURE;
    }

    pnd = nfc_open(context, NULL);
    if (!pnd) {
        fprintf(stderr, "Не вдалося відкрити NFC-зчитувач\n");
        nfc_exit(context);
        return EXIT_FAILURE;
    }

    if (nfc_initiator_init(pnd) < 0) {
        nfc_perror(pnd, "nfc_initiator_init");
        nfc_close(pnd);
        nfc_exit(context);
        return EXIT_FAILURE;
    }

    /* Команда ISO 7816-4 SELECT AID */
    const uint8_t select_aid[] = {
        0x00, 0xA4, 0x04, 0x00, 0x07,
        0xA0, 0x00, 0x00, 0x00, 0x04, 0x10, 0x10
    };

    nfc_apdu_response_t response;
    memset(&response, 0, sizeof(response));

    printf("Надсилання APDU та вимірювання затримки RTT...\n");
    if (nfc_send_apdu_with_timing(pnd, select_aid, sizeof(select_aid), &response)) {
        printf("Отримано %zx байтів. Виміряний RTT: %lld мкс\n", 
               response.length, (long long)response.rtt_microseconds);

        if (response.rtt_microseconds > MAX_ALLOWED_RTT_US) {
            printf("[УВАГА! АТАКА] Затримка %lld мкс перевищує поріг %ld мкс! "
                   "Сесію заблоковано (виявлено ретрансляцію).\n",
                   (long long)response.rtt_microseconds, MAX_ALLOWED_RTT_US);
        } else {
            printf("[OK] Затримка в межах норми. Тег знаходиться поруч.\n");
        }
    }

    nfc_close(pnd);
    nfc_exit(context);
    return EXIT_SUCCESS;
}
