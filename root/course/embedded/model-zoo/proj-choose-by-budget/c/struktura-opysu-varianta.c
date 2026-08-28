#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

// Один варіант родини (n/s/m/l/x). Усе цілочисельне — прошивка не любить float
// там, де можна без нього: час у мкс, пам'ять у байтах, mAP у сотих.
typedef struct {
    const char*    name;            // "n", "s", "m", "l", "x" — для логів
    const uint8_t* model_data;      // .tflite, вшитий у Flash (або 0, якщо не залитий)
    uint32_t       model_bytes;     // вага int8-моделі = скільки Flash займе
    uint32_t       arena_bytes;     // потрібна тензорна арена = скільки RAM з'їсть
    uint16_t       map_x100;        // точність mAP × 100 (напр., 5020 = 50.2) — для звіту
    uint32_t       latency_us;      // ВИМІРЯНИЙ час проходу (p99) на ЦЬОМУ чипі!
} ModelVariant;
