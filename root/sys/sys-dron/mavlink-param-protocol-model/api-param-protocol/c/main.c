#include <stdint.h>
#include <string.h>
#include <stdbool.h>

// Уніфікований двійковий контейнер для пакування значень у 4 байти
typedef union {
    float    f32;
    uint32_t u32;
    int32_t  i32;
    uint16_t u16;
    int16_t  i16;
    uint8_t  u8;
    int8_t   i8;
    uint8_t  raw_bytes[4];
} mav_param_union_t;

// Безпечне читання param_id у буфер розміром 17 байтів
void extract_param_id(const char wire_id[16], char out_buf[17]) {
    memcpy(out_buf, wire_id, 16);
    out_buf[16] = '\0';
}

// Запис значення цілого числа в контейнер PARAM_SET / PARAM_VALUE
float pack_uint32_value(uint32_t val) {
    mav_param_union_t u;
    u.u32 = val;
    return u.f32;
}

// Вилучення 32-бітного цілого числа без втрати мантиси
uint32_t unpack_uint32_value(float wire_float) {
    mav_param_union_t u;
    u.f32 = wire_float;
    return u.u32;
}
