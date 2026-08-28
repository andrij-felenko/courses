#include <stdint.h>

/* Потокове кодування часової мітки за схемою Delta-of-Delta */
typedef struct {
    uint64_t prev_time;
    uint64_t prev_delta;
    uint32_t sample_count;
} TimestampEncoder;

void ts_encoder_init(TimestampEncoder *enc) {
    enc->prev_time = 0;
    enc->prev_delta = 0;
    enc->sample_count = 0;
}

/* Обчислення довжини та бітового коду для DOD */
int encode_timestamp_step(TimestampEncoder *enc, uint64_t t, 
                          uint64_t *out_bits, int *out_bit_len) {
    if (enc->sample_count == 0) {
        *out_bits = t;
        *out_bit_len = 64;
        enc->prev_time = t;
        enc->sample_count++;
        return 0;
    }
    
    uint64_t delta = t - enc->prev_time;
    if (enc->sample_count == 1) {
        *out_bits = delta;
        *out_bit_len = 14;
        enc->prev_delta = delta;
        enc->prev_time = t;
        enc->sample_count++;
        return 0;
    }
    
    int64_t dod = (int64_t)delta - (int64_t)enc->prev_delta;
    enc->prev_delta = delta;
    enc->prev_time = t;
    enc->sample_count++;

    if (dod == 0) {
        *out_bits = 0; /* Біт '0' */
        *out_bit_len = 1;
    } else if (dod >= -63 && dod <= 64) {
        /* Префікс '10' (2 біти) + 7 бітів значення */
        *out_bits = (2ULL << 7) | ((uint64_t)dod & 0x7F);
        *out_bit_len = 9;
    } else if (dod >= -255 && dod <= 256) {
        /* Префікс '110' (3 біти) + 9 бітів значення */
        *out_bits = (6ULL << 9) | ((uint64_t)dod & 0x1FF);
        *out_bit_len = 12;
    } else if (dod >= -2047 && dod <= 2048) {
        /* Префікс '1110' (4 біти) + 12 бітів значення */
        *out_bits = (14ULL << 12) | ((uint64_t)dod & 0xFFF);
        *out_bit_len = 16;
    } else {
        /* Префікс '1111' (4 біти) + 32 біти значення */
        *out_bits = (15ULL << 32) | ((uint32_t)dod);
        *out_bit_len = 36;
    }
    return 0;
}
