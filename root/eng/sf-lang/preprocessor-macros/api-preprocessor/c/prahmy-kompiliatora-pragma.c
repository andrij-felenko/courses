#include <stdio.h>

/* Вказівка компілятору запакувати поля без вирівнювання (1 байт) */
#pragma pack(push, 1)
typedef struct {
    unsigned char flag;
    unsigned int  data;
} CompactHeader;
#pragma pack(pop)

/* Застосування _Pragma всередині функціонального макросу */
#define SUPPRESS_DEPRECATED_WARNING \
    _Pragma("GCC diagnostic push") \
    _Pragma("GCC diagnostic ignored \"-Wdeprecated-declarations\"")

int main(void) {
    printf("Розмір CompactHeader: %zu байтів\n", sizeof(CompactHeader));
    return 0;
}
