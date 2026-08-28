#include <stdio.h>

// Усі затримки — у мілісекундах
typedef struct {
    float sensor;    // набір кадру сенсором
    float encode;    // стиснення кодеком (0 для аналогу)
    float radio;     // ефір + демодуляція
    float decode;    // розпакування (0 для аналогу)
    float display;   // вивід на екран окулярів
} latency_ms;

float glass_to_glass(latency_ms p) {
    return p.sensor + p.encode + p.radio + p.decode + p.display;
}

// Скільки метрів апарат пролетить за час затримки
float blind_distance_m(float latency_ms, float speed_kmh) {
    float speed_ms = speed_kmh / 3.6f;        // км/год → м/с
    return speed_ms * (latency_ms / 1000.0f); // мс → с
}

int main(void) {
    latency_ms o4 = { .sensor=7, .encode=12, .radio=4, .decode=6, .display=8 };
    float total = glass_to_glass(o4);              // 37.0 мс
    float blind = blind_distance_m(total, 120.0f); // на 120 км/год

    printf("Затримка: %.1f мс\n", total);
    printf("Наосліп:  %.2f м\n", blind);
    return 0;
}
