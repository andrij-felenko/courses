#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <assert.h>

/* Функція-ціль для LLVM LibFuzzer */
static void dummy_callback(const uint8_t *data, size_t len, void *ctx) {
    /* Перевіряємо, що отримані дані доступні для читання */
    volatile uint8_t checksum = 0;
    for (size_t i = 0; i < len; ++i) {
        checksum ^= data[i];
    }
    (void)checksum;
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    uint8_t buffer[1024];
    slip_decoder_t dec;
    slip_decoder_init(&dec, buffer, sizeof(buffer), dummy_callback, NULL);

    for (size_t i = 0; i < size; ++i) {
        slip_decoder_feed_byte(&dec, data[i]);
    }

    return 0;
}
