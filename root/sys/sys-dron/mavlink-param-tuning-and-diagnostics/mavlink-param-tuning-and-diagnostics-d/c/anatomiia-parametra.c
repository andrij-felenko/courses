#include <stdint.h>
#include <string.h>
#include <stdbool.h>

// Пакування цілого числа uint32_t у 4-байтове поле param_value без втрати бітів
float pack_uint32_param(uint32_t val) {
    float param_container;
    memcpy(&param_container, &val, sizeof(float));
    return param_container;
}

// Розпакування значення param_value відповідно до переданого типу MAV_PARAM_TYPE
bool unpack_param_to_uint32(float raw_value, uint8_t param_type, uint32_t *out_val) {
    if (param_type == 5 /* MAV_PARAM_TYPE_UINT32 */) {
        memcpy(out_val, &raw_value, sizeof(uint32_t));
        return true;
    } else if (param_type == 1 /* MAV_PARAM_TYPE_UINT8 */) {
        uint8_t temp;
        memcpy(&temp, &raw_value, sizeof(uint8_t));
        *out_val = temp;
        return true;
    }
    return false;
}
