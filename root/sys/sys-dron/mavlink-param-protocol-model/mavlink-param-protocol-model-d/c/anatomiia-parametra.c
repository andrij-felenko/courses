#include <stdint.h>
#include <string.h>
#include <stdbool.h>

// Безпечне пакування uint32_t у 4-байтове поле float через побітове копіювання
float pack_param_uint32(uint32_t val) {
    float container;
    memcpy(&container, &val, sizeof(float));
    return container;
}

// Вилучення uint32_t із контейнера float без втрати молодших бітів
uint32_t unpack_param_uint32(float container) {
    uint32_t val;
    memcpy(&val, &container, sizeof(uint32_t));
    return val;
}

// Безпечне копіювання імені параметра з гарантованим нульовим термінатором
void safe_get_param_id(const char wire_id[16], char out_buf[17]) {
    memcpy(out_buf, wire_id, 16);
    out_buf[16] = '\0';
}
