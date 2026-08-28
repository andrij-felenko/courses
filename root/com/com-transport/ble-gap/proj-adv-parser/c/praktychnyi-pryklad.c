#include <stdio.h>

/* Структура розібраного звіту давача */
typedef struct {
    char    device_name[32];
    bool    has_name;
    int16_t temperature_centi_celsius;
    uint8_t humidity_pct;
    uint8_t battery_pct;
    bool    has_telemetry;
} sensor_report_t;

/* Callback обробника одного TLV блоку */
static bool sensor_ad_visitor(const ble_ad_element_t* elem, void* user_ctx) {
    sensor_report_t* report = (sensor_report_t*)user_ctx;

    if (elem->type == BLE_AD_TYPE_COMPLETE_LOCAL_NAME) {
        /* Копіюємо ім'я з гарантією завершального нуля та захистом від переповнення */
        size_t copy_len = (elem->data_len < sizeof(report->device_name) - 1) 
                          ? elem->data_len 
                          : sizeof(report->device_name) - 1;
        
        for (size_t i = 0; i < copy_len; ++i) {
            uint8_t ch = elem->data[i];
            /* Санітизація: замінюємо керуючі символи на пробіл */
            report->device_name[i] = (ch >= 0x20 && ch <= 0x7E) ? (char)ch : ' ';
        }
        report->device_name[copy_len] = '\0';
        report->has_name = true;
    }
    else if (elem->type == BLE_AD_TYPE_MANUFACTURER_SPECIFIC) {
        /* Перевіряємо мінімальну довжину: 2 байти Company ID + 4 байти сенсорів = 6 Б */
        if (elem->data_len >= 6) {
            /* Безпечне зчитування Company ID у форматі Little-Endian */
            uint16_t company_id = (uint16_t)elem->data[0] | ((uint16_t)elem->data[1] << 8);

            if (company_id == 0x02E5) { /* Espressif Systems */
                /* Зчитуємо температуру без виникнення Unaligned Access Fault */
                int16_t raw_temp = (int16_t)((uint16_t)elem->data[2] | ((uint16_t)elem->data[3] << 8));
                report->temperature_centi_celsius = raw_temp;
                report->humidity_pct = elem->data[4];
                report->battery_pct  = elem->data[5];
                report->has_telemetry = true;
            }
        }
    }

    return true; /* Продовжуємо обхід наступних блоків */
}

void process_adv_packet(const uint8_t* raw_adv_data, size_t raw_len) {
    sensor_report_t report;
    memset(&report, 0, sizeof(report));

    ble_ad_parse(raw_adv_data, raw_len, sensor_ad_visitor, &report);

    if (report.has_name) {
        printf("Знайдено пристрій: %s\n", report.device_name);
    }
    if (report.has_telemetry) {
        printf("Телеметрія: T = %.2f °C, Вологість = %u %%, Заряд = %u %%\n",
               report.temperature_centi_celsius / 100.0f,
               report.humidity_pct,
               report.battery_pct);
    }
}
