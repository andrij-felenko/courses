#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

typedef struct {
    uint16_t sensor_id;
    uint32_t timestamp;
    double*  readings;
    int      reading_count;
} TelemetryRecord;

/* Застаріла C-функція парсингу бінарного кадру */
int parse_telemetry_packet_c(const uint8_t* raw_buffer, int buffer_size,
                            TelemetryRecord** out_record, void* logger_ctx) {
    if (!raw_buffer || buffer_size < 12) {
        return -1; // Недостатній розмір заголовка
    }

    // 1. Перевірка магічного числа 0x54454C4D ("TELM")
    uint32_t magic = *(uint32_t*)raw_buffer;
    if (magic != 0x54454C4D) {
        return -2;
    }

    // 2. Небезпечні звужуючі касти та адресна арифметика
    uint16_t sensor_id = *(uint16_t*)(raw_buffer + 4);
    uint16_t payload_len = *(uint16_t*)(raw_buffer + 6);
    uint32_t timestamp = *(uint32_t*)(raw_buffer + 8);

    if (buffer_size < 12 + payload_len + 4) {
        return -3; // Пошкоджений пакет: payload виходить за межі буфера
    }

    // 3. Ручне виділення пам'яті через malloc
    TelemetryRecord* rec = (TelemetryRecord*)malloc(sizeof(TelemetryRecord));
    if (!rec) return -4;

    rec->sensor_id = sensor_id;
    rec->timestamp = timestamp;
    rec->reading_count = payload_len / sizeof(double);
    rec->readings = NULL;

    if (rec->reading_count > 0) {
        rec->readings = (double*)malloc(rec->reading_count * sizeof(double));
        if (!rec->readings) {
            free(rec); // Ручне вивільнення при збої
            return -4;
        }

        // Копіювання з сирого зсуву покажчика
        memcpy(rec->readings, raw_buffer + 12, rec->reading_count * sizeof(double));
    }

    *out_record = rec;
    return 0; // Успіх
}
