// Обчислення об'єму за кубічним сплайном (C / ESP-IDF)
#include <stdio.h>
#include <stddef.h>

typedef struct {
    float h; // Початковий рівень інтервалу (см)
    float a; // Коефіцієнт a_i (об'єм у точці h_i, л)
    float b; // Коефіцієнт b_i (л/см)
    float c; // Коефіцієнт c_i (л/см²)
    float d; // Коефіцієнт d_i (л/см³)
} spline_segment_t;

typedef struct {
    const spline_segment_t *segments;
    size_t count; // Кількість сегментів
} spline_table_t;

// Обчислення об'єму за схемою Горнера
float spline_evaluate(const spline_table_t *table, float h) {
    if (table == NULL || table->count == 0) {
        return 0.0f;
    }
    // Обмеження за межами калібрувального діапазону
    if (h <= table->segments[0].h) {
        return table->segments[0].a;
    }
    size_t last = table->count - 1;
    if (h >= table->segments[last].h) {
        return table->segments[last].a;
    }

    // Двійковий пошук інтервалу h_i <= h < h_{i+1}
    size_t low = 0;
    size_t high = table->count - 1;
    size_t idx = 0;

    while (low <= high) {
        size_t mid = low + (high - low) / 2;
        if (table->segments[mid].h <= h) {
            idx = mid;
            low = mid + 1;
        } else {
            if (mid == 0) break;
            high = mid - 1;
        }
    }

    // Схема Горнера: V = a + dx * (b + dx * (c + dx * d))
    float dx = h - table->segments[idx].h;
    return table->segments[idx].a + dx * (table->segments[idx].b + dx * (table->segments[idx].c + dx * table->segments[idx].d));
}
