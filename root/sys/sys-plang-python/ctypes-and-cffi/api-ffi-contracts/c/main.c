// point_struct.h
#include <stdint.h>

typedef struct {
    int32_t x;
    int32_t y;
    double  weight;
    uint8_t flags;
    // Компілятор додає 7 байтів padding у кінці, щоб загальний розмір структури
    // був кратний максимальному вирівнюванню поля double (8 байтів).
} PointRecord;

typedef union {
    uint32_t as_uint;
    float    as_float;
    uint8_t  as_bytes[4];
} FloatIntUnion;
