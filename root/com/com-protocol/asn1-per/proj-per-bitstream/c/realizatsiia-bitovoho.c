#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Структура для побітового запису даних */
typedef struct {
    uint8_t *buffer;
    size_t capacity_bytes;
    size_t bit_pos;       /* Поточна позиція в бітах від початку буфера */
} BitWriter;

/* Ініціалізація записувача */
void bit_writer_init(BitWriter *bw, uint8_t *buf, size_t cap) {
    bw->buffer = buf;
    bw->capacity_bytes = cap;
    bw->bit_pos = 0;
    if (cap > 0) {
        memset(buf, 0, cap);
    }
}

/* Запис до 32 бітів у потік (MSB-first) */
bool bit_writer_put_bits(BitWriter *bw, uint32_t value, uint8_t num_bits) {
    if (num_bits == 0) return true;
    if (num_bits > 32) return false;
    if ((bw->bit_pos + num_bits) > (bw->capacity_bytes * 8)) return false;

    /* Маскуємо зайві старші біти */
    if (num_bits < 32) {
        value &= (1U << num_bits) - 1U;
    }

    int remaining = num_bits;
    while (remaining > 0) {
        size_t byte_idx = bw->bit_pos / 8;
        uint8_t bit_in_byte = bw->bit_pos % 8;
        uint8_t bits_free_in_byte = 8 - bit_in_byte;

        uint8_t bits_to_write = (remaining < bits_free_in_byte) ? (uint8_t)remaining : bits_free_in_byte;
        uint8_t shift = remaining - bits_to_write;
        uint8_t chunk = (uint8_t)((value >> shift) & ((1U << bits_to_write) - 1U));

        /* Зсуваємо фрагмент на потрібну позицію в поточному байті */
        bw->buffer[byte_idx] |= (uint8_t)(chunk << (bits_free_in_byte - bits_to_write));

        bw->bit_pos += bits_to_write;
        remaining -= bits_to_write;
    }
    return true;
}

/* Запис 1 біта */
bool bit_writer_put_bit(BitWriter *bw, bool bit) {
    return bit_writer_put_bits(bw, bit ? 1U : 0U, 1);
}

/* Запис обмеженого цілого числа [lb .. ub] */
bool bit_writer_put_constrained_int(BitWriter *bw, int64_t val, int64_t lb, int64_t ub) {
    if (val < lb || val > ub) return false;
    uint64_t range = (uint64_t)(ub - lb + 1);
    if (range == 1) return true; /* Константа: 0 бітів */

    /* Обчислюємо ceil(log2(range)) */
    uint8_t bits = 0;
    uint64_t temp = range - 1;
    while (temp > 0) {
        bits++;
        temp >>= 1;
    }

    uint64_t offset = (uint64_t)(val - lb);
    if (bits <= 32) {
        return bit_writer_put_bits(bw, (uint32_t)offset, bits);
    } else {
        /* Якщо діапазон більше 32 бітів, пишемо двома частинами */
        uint8_t high_bits = bits - 32;
        if (!bit_writer_put_bits(bw, (uint32_t)(offset >> 32), high_bits)) return false;
        return bit_writer_put_bits(bw, (uint32_t)(offset & 0xFFFFFFFFU), 32);
    }
}

/* Вирівнювання на найближчу межу октету (для APER та Open Type) */
void bit_writer_align_to_byte(BitWriter *bw) {
    size_t rem = bw->bit_pos % 8;
    if (rem != 0) {
        bw->bit_pos += (8 - rem);
    }
}

/* Отримання кількості повних байтів після завершення */
size_t bit_writer_get_length_bytes(const BitWriter *bw) {
    return (bw->bit_pos + 7) / 8;
}

/* Структура для побітового читання */
typedef struct {
    const uint8_t *buffer;
    size_t total_bits;
    size_t bit_pos;
} BitReader;

/* Ініціалізація читача */
void bit_reader_init(BitReader *br, const uint8_t *buf, size_t total_bytes) {
    br->buffer = buf;
    br->total_bits = total_bytes * 8;
    br->bit_pos = 0;
}

/* Читання до 32 бітів */
bool bit_reader_get_bits(BitReader *br, uint8_t num_bits, uint32_t *out_val) {
    if (num_bits == 0) { *out_val = 0; return true; }
    if (num_bits > 32) return false;
    if (br->bit_pos + num_bits > br->total_bits) return false;

    uint32_t result = 0;
    int remaining = num_bits;
    while (remaining > 0) {
        size_t byte_idx = br->bit_pos / 8;
        uint8_t bit_in_byte = br->bit_pos % 8;
        uint8_t bits_avail_in_byte = 8 - bit_in_byte;

        uint8_t bits_to_read = (remaining < bits_avail_in_byte) ? (uint8_t)remaining : bits_avail_in_byte;
        uint8_t shift = bits_avail_in_byte - bits_to_read;
        uint8_t mask = (1U << bits_to_read) - 1U;
        uint8_t chunk = (br->buffer[byte_idx] >> shift) & mask;

        result = (result << bits_to_read) | chunk;
        br->bit_pos += bits_to_read;
        remaining -= bits_to_read;
    }
    *out_val = result;
    return true;
}

/* Читання 1 біта */
bool bit_reader_get_bit(BitReader *br, bool *out_bit) {
    uint32_t val = 0;
    if (!bit_reader_get_bits(br, 1, &val)) return false;
    *out_bit = (val != 0);
    return true;
}

/* Читання обмеженого цілого числа [lb .. ub] */
bool bit_reader_get_constrained_int(BitReader *br, int64_t lb, int64_t ub, int64_t *out_val) {
    uint64_t range = (uint64_t)(ub - lb + 1);
    if (range == 1) {
        *out_val = lb;
        return true;
    }

    uint8_t bits = 0;
    uint64_t temp = range - 1;
    while (temp > 0) {
        bits++;
        temp >>= 1;
    }

    if (bits <= 32) {
        uint32_t raw = 0;
        if (!bit_reader_get_bits(br, bits, &raw)) return false;
        *out_val = lb + (int64_t)raw;
        return (*out_val <= ub);
    } else {
        uint8_t high_bits = bits - 32;
        uint32_t raw_high = 0, raw_low = 0;
        if (!bit_reader_get_bits(br, high_bits, &raw_high)) return false;
        if (!bit_reader_get_bits(br, 32, &raw_low)) return false;
        uint64_t raw = (((uint64_t)raw_high) << 32) | raw_low;
        *out_val = lb + (int64_t)raw;
        return (*out_val <= ub);
    }
}

/* Пропуск вирівнювання на межу октету */
void bit_reader_align_to_byte(BitReader *br) {
    size_t rem = br->bit_pos % 8;
    if (rem != 0) {
        br->bit_pos += (8 - rem);
    }
}
