#include <stdio.h>
#include <string.h>
#include <stdint.h>

// Структура телеметрії з датчиків
typedef struct {
    uint16_t sensor_id; // Може містити 0x0D0A при конкретних значеннях
    float temperature;  // Містить довільні плаваючі байти
    uint8_t flags;
} __attribute__((packed)) SensorPayload;

void demonstrate_binary_hazard(const SensorPayload* data) {
    const uint8_t* raw_bytes = (const uint8_t*)data;
    size_t size = sizeof(SensorPayload);

    // Імітація текстового AT-парсера: пошук \r\n у потоці
    for (size_t i = 0; i < size - 1; i++) {
        if (raw_bytes[i] == 0x0D && raw_bytes[i + 1] == 0x0A) {
            // КРИТИЧНА ПОМИЛКА: Парсер хибно зріже кадри на і-тому байті!
            printf("[ЗБОЙ PARSER] Виявлено хибний термінатор CRLF на зсуві %zu\n", i);
            return;
        }
    }
    printf("[OK] Потік не містить CRLF, але це не гарантовано для всіх даних\n");
}
