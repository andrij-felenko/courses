#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BLE_LEGACY_ADV_MAX_PAYLOAD 31

typedef struct {
    uint8_t buffer[BLE_LEGACY_ADV_MAX_PAYLOAD];
    size_t  current_len;
} ble_adv_builder_t;

void ble_adv_builder_init(ble_adv_builder_t* builder) {
    if (builder) {
        memset(builder->buffer, 0, sizeof(builder->buffer));
        builder->current_len = 0;
    }
}

/**
 * @brief Додавання довільного TLV блоку до рекламного кадру.
 * @return true, якщо блок успішно вмістився в ліміт 31 байта.
 */
bool ble_adv_builder_add_field(ble_adv_builder_t* builder, uint8_t type, 
                              const uint8_t* data, uint8_t data_len) 
{
    if (!builder || (!data && data_len > 0)) {
        return false;
    }

    /* Розрахунок необхідного місця: 1 байт (Length) + 1 байт (Type) + data_len */
    size_t required_space = 2 + data_len;

    if (builder->current_len + required_space > BLE_LEGACY_ADV_MAX_PAYLOAD) {
        return false; /* Переповнення буфера */
    }

    /* Запис поля довжини (Type + data_len) */
    builder->buffer[builder->current_len] = (uint8_t)(1 + data_len);
    builder->buffer[builder->current_len + 1] = type;

    if (data_len > 0) {
        memcpy(&builder->buffer[builder->current_len + 2], data, data_len);
    }

    builder->current_len += required_space;
    return true;
}

bool ble_adv_builder_add_flags(ble_adv_builder_t* builder, uint8_t flags) {
    return ble_adv_builder_add_field(builder, BLE_AD_TYPE_FLAGS, &flags, 1);
}

bool ble_adv_builder_add_name(ble_adv_builder_t* builder, const char* name) {
    if (!name) return false;
    return ble_adv_builder_add_field(builder, BLE_AD_TYPE_COMPLETE_LOCAL_NAME, 
                                     (const uint8_t*)name, (uint8_t)strlen(name));
}
