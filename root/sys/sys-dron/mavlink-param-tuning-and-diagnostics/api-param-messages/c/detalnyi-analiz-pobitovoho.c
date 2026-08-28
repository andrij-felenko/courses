#include <stdint.h>
#include <string.h>

/* Безпечне пакування uint32 у float контейнер */
float pack_uint32_to_mavlink_float(uint32_t val) {
    float f;
    memcpy(&f, &val, sizeof(float));
    return f;
}

/* Безпечне розпакування float контейнера у uint32 */
uint32_t unpack_mavlink_float_to_uint32(float f) {
    uint32_t val;
    memcpy(&val, &f, sizeof(uint32_t));
    return val;
}

/* Безпечне розпакування float контейнера у int32 */
int32_t unpack_mavlink_float_to_int32(float f) {
    int32_t val;
    memcpy(&val, &f, sizeof(int32_t));
    return val;
}
