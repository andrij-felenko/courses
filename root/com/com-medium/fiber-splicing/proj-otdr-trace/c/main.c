#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

// Типи оптичних подій на трасі
typedef enum {
    EVENT_NONE = 0,
    EVENT_SPLICE_FUSION,
    EVENT_CONNECTOR,
    EVENT_GAINER,
    EVENT_FIBER_END
} otdr_event_type_t;

// Структура опису знайденої події
typedef struct {
    double distance_m;
    otdr_event_type_t type;
    double loss_db;
    double return_loss_db;
} otdr_event_t;

// Вхідний масив відліків траси
typedef struct {
    const double *distances_m;
    const double *powers_dbm;
    size_t count;
    double pulse_width_ns;
} otdr_trace_t;

// Функція аналізу траси рефлектометра
size_t analyze_otdr_trace(const otdr_trace_t *trace,
                         otdr_event_t *out_events,
                         size_t max_events,
                         double noise_floor_dbm) {
    if (!trace || !out_events || trace->count < 5) {
        return 0;
    }

    size_t event_count = 0;
    double backscatter_slope = 0.0002; // ~0.2 дБ/км

    for (size_t i = 2; i < trace->count - 2; ++i) {
        double dist = trace->distances_m[i];
        double p_prev = trace->powers_dbm[i - 1];
        double p_curr = trace->powers_dbm[i];
        double p_next = trace->powers_dbm[i + 1];

        // Перевірка на кінець волокна (сигнал впав до рівня шумів)
        if (p_curr <= noise_floor_dbm && p_prev > noise_floor_dbm) {
            if (event_count < max_events) {
                out_events[event_count++] = (otdr_event_t){
                    .distance_m = dist,
                    .type = EVENT_FIBER_END,
                    .loss_db = p_prev - noise_floor_dbm,
                    .return_loss_db = 0.0
                };
            }
            break;
        }

        // Перевірка на відбивний пік (конектор)
        if (p_curr > p_prev + 0.5 && p_curr > p_next + 0.5) {
            double p_after = trace->powers_dbm[i + 3];
            double loss = p_prev - p_after;
            double rl = p_curr - p_prev + 10.0 * log10(trace->pulse_width_ns);

            if (event_count < max_events) {
                out_events[event_count++] = (otdr_event_t){
                    .distance_m = dist,
                    .type = EVENT_CONNECTOR,
                    .loss_db = loss,
                    .return_loss_db = rl
                };
            }
            i += 3; // Пропускаємо мертву зону відбиття
            continue;
        }

        // Перевірка на невідбивну сходинку (зварний шов або гейнер)
        double step = p_prev - p_next - (trace->distances_m[i + 1] - trace->distances_m[i - 1]) * backscatter_slope;
        if (fabs(step) >= 0.03) { // Поріг чутливості 0.03 дБ
            otdr_event_type_t ev_type = (step > 0) ? EVENT_SPLICE_FUSION : EVENT_GAINER;

            if (event_count < max_events) {
                out_events[event_count++] = (otdr_event_t){
                    .distance_m = dist,
                    .type = ev_type,
                    .loss_db = step,
                    .return_loss_db = 0.0
                };
            }
            i += 2;
        }
    }

    return event_count;
}

int main(void) {
    // Тестовий профіль траси: 3000 м, зварка на 1000 м, конектор на 2000 м
    double dists[] = {0, 500, 999, 1000, 1001, 1500, 1999, 2000, 2001, 2005, 2500, 3000};
    double powers[] = {0.0, -0.1, -0.2, -0.25, -0.25, -0.35, -0.45, +12.0, -0.85, -0.86, -0.96, -110.0};
    size_t count = sizeof(dists) / sizeof(dists[0]);

    otdr_trace_t trace = {
        .distances_m = dists,
        .powers_dbm = powers,
        .count = count,
        .pulse_width_ns = 50.0
    };

    otdr_event_t events[10];
    size_t found = analyze_otdr_trace(&trace, events, 10, -100.0);

    printf("Знайдено оптичних подій: %zu\n", found);
    for (size_t i = 0; i < found; ++i) {
        const char *tname = "Невідомо";
        switch (events[i].type) {
            case EVENT_SPLICE_FUSION: tname = "Зварний шов"; break;
            case EVENT_CONNECTOR:     tname = "Конектор"; break;
            case EVENT_GAINER:        tname = "Гейнер (підйом)"; break;
            case EVENT_FIBER_END:     tname = "Кінець волокна"; break;
            default: break;
        }
        printf("Подія на %.1f м: тип=%s, втрати=%.3f дБ, RL=%.1f дБ\n",
               events[i].distance_m, tname, events[i].loss_db, events[i].return_loss_db);
    }

    return 0;
}
