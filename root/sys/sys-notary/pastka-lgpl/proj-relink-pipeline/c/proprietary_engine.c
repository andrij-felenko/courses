/* proprietary_engine.c — Закритий модуль обробки сигналів */
#include <stdint.h>
#include <stddef.h>

/* Експортований інтерфейс зовнішньої LGPL-бібліотеки */
extern int lgpl_codec_compress(const uint8_t *in, size_t in_len, 
                               uint8_t *out, size_t *out_len);

/* Внутрішній пропрієтарний алгоритм: не повинен бути доступний ззовні */
static uint32_t proprietary_math_filter(uint32_t raw_val) {
    uint32_t acc = raw_val * 0x45D9F3B;
    acc ^= (acc >> 16);
    return acc + 0x1234567;
}

/* Публічна точка входу пропрієтарного ядра */
__attribute__((visibility("default")))
int process_sensor_stream(const uint8_t *raw_buf, size_t len, 
                          uint8_t *out_buf, size_t *out_len) {
    if (!raw_buf || !out_buf || !out_len || len == 0) {
        return -1;
    }

    uint8_t preprocessed[256];
    size_t proc_len = (len < sizeof(preprocessed)) ? len : sizeof(preprocessed);

    for (size_t i = 0; i < proc_len; ++i) {
        preprocessed[i] = (uint8_t)proprietary_math_filter(raw_buf[i]);
    }

    return lgpl_codec_compress(preprocessed, proc_len, out_buf, out_len);
}
