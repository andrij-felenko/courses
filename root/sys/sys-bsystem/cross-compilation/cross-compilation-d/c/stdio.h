#include <stdio.h>
#include <stddef.h>
#include <stdint.h>

struct NetworkPacket {
    uint32_t header;
    uint64_t payload;
    uint16_t footer;
};

// Захист на етапі компіляції від неочікуваного вирівнювання
_Static_assert(sizeof(struct NetworkPacket) == 24, "Розмір структури не відповідає стандарту ARM AAPCS!");
_Static_assert(offsetof(struct NetworkPacket, payload) == 8, "Зміщення поля payload порушено!");
