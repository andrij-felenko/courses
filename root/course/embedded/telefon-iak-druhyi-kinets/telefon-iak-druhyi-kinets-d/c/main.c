#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Структура бінарного кадру телеметрії (фіксований порядок байтів Little-Endian) */
typedef struct __attribute__((packed)) {
    int16_t  temperature_centi_c; /* Температура в сотих градуса (наприклад, 2450 = 24.50 °C) */
    uint16_t battery_voltage_mv;   /* Напруга живлення в мілівольтах (наприклад, 3300 мВ) */
    uint32_t sequence_number;      /* Порядковий номер пакета для контролю втрат */
} telemetry_payload_t;

/* Стан підписки та активного з'єднання */
typedef struct {
    uint16_t conn_handle;
    uint16_t telemetry_val_handle;
    uint16_t telemetry_cccd_handle;
    uint16_t command_val_handle;
    uint16_t negotiated_mtu;
    bool     notifications_enabled;
    bool     is_connected;
} ble_gatt_server_ctx_t;

static ble_gatt_server_ctx_t g_server_ctx = {
    .conn_handle = 0xFFFF,
    .negotiated_mtu = 23, /* Базовий ATT MTU до узгодження */
    .notifications_enabled = false,
    .is_connected = false,
};

static telemetry_payload_t g_latest_telemetry = {
    .temperature_centi_c = 2500,
    .battery_voltage_mv = 3300,
    .sequence_number = 0,
};

/* Зворотний виклик на читання значення характеристики телеметрії */
int gatt_svr_read_telemetry_cb(uint16_t conn_handle, uint16_t attr_handle,
                              void *out_buf, uint16_t max_len, uint16_t *out_len) {
    if (max_len < sizeof(telemetry_payload_t)) {
        return -1; /* Буфер клієнта замалий */
    }
    memcpy(out_buf, &g_latest_telemetry, sizeof(telemetry_payload_t));
    *out_len = sizeof(telemetry_payload_t);
    return 0; /* ATT_SUCCESS */
}

/* Зворотний виклик на запис у дескриптор CCCD (підписка/відписка) */
int gatt_svr_write_cccd_cb(uint16_t conn_handle, uint16_t attr_handle,
                          const uint8_t *data, uint16_t len) {
    if (len != 2) {
        return -1; /* Помилка довжини атрибута ATT_ERR_INVALID_ATTR_VALUE_LEN */
    }

    uint16_t cccd_val = (uint16_t)data[0] | ((uint16_t)data[1] << 8);
    g_server_ctx.notifications_enabled = (cccd_val & 0x0001) != 0;

    return 0; /* ATT_SUCCESS */
}

/* Зворотний виклик на запис команди зі смартфона */
int gatt_svr_write_command_cb(uint16_t conn_handle, uint16_t attr_handle,
                             const uint8_t *data, uint16_t len) {
    if (len < 1) {
        return -1;
    }

    uint8_t cmd_opcode = data[0];
    switch (cmd_opcode) {
        case 0x01: /* Скидання лічильника */
            g_latest_telemetry.sequence_number = 0;
            break;
        case 0x02: /* Запис нового порогу або конфігурації */
            if (len >= 3) {
                /* Обробка додаткових байтів конфігурації */
            }
            break;
        default:
            return -2; /* Невідома команда */
    }

    return 0;
}

/* Відправка асинхронного сповіщення телеметрії на смартфон */
bool ble_gatt_server_send_telemetry(int16_t temp_c, uint16_t vbatt_mv) {
    if (!g_server_ctx.is_connected || !g_server_ctx.notifications_enabled) {
        return false; /* Клієнт не підключений або не підписався через CCCD */
    }

    /* Оновлення глобальних даних */
    g_latest_telemetry.temperature_centi_c = temp_c;
    g_latest_telemetry.battery_voltage_mv = vbatt_mv;
    g_latest_telemetry.sequence_number++;

    /* Перевірка, чи вміщується корисне навантаження в поточний узгоджений MTU */
    if (sizeof(telemetry_payload_t) > (g_server_ctx.negotiated_mtu - 3)) {
        return false; /* Потрібна фрагментація або збільшення MTU */
    }

    /* Виклик низькорівневого стекового API надсилання Notify */
    /* Псевдокод системного виклику: ble_gatts_notify_custom(conn_handle, val_handle, buf, len) */
    return true;
}

/* Обробник події оновлення MTU */
void ble_gatt_on_mtu_updated(uint16_t conn_handle, uint16_t new_mtu) {
    if (g_server_ctx.conn_handle == conn_handle) {
        g_server_ctx.negotiated_mtu = new_mtu;
    }
}
