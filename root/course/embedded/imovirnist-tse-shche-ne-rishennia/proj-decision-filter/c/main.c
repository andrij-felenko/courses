/* Демонстрація фільтра впевненості: траса одного треку такт за тактом,
 * далі — пул із кількох треків і його поведінка на зникненні об'єкта.
 * Збірка: cc -std=c11 -O2 -Wall -Wextra *.c -lm -o decision_filter */

#include "track_pool.h"

#include <stdio.h>

#define TICK_MS 50U

/* Пороги з розбору в статті: alpha = 0.75, H_on = 0.70, H_off = 0.35,
 * утримання 200 мс, голосування 3 з 5. */
static const ConfidenceFilterConfig FILTER_CFG = {
    .temperature     = 2.0f,
    .alpha           = 0.75f,
    .thresh_on       = 0.70f,
    .thresh_off      = 0.35f,
    .min_hold_ms     = 200U,
    .window_size     = 5U,
    .min_votes       = 3U,
    .fail_safe_start = false,
};

static void format_window(uint32_t window, unsigned bits, char *out) {
    for (unsigned i = 0; i < bits; ++i) {
        out[i] = ((window >> (bits - 1U - i)) & 1U) ? '1' : '0';
    }
    out[bits] = '\0';
}

/* Траса: одиночний спалах шуму, потім справжня перешкода з провалом детекції. */
static void demo_trace(void) {
    static const float probs[] = {
        0.05f, 0.95f, 0.04f, 0.85f, 0.90f, 0.88f, 0.10f, 0.92f, 0.05f, 0.02f
    };
    const unsigned ticks = (unsigned)(sizeof probs / sizeof probs[0]);

    ConfidenceFilter filter;
    if (!confidence_filter_init(&filter, &FILTER_CFG, 0U)) {
        fprintf(stderr, "Непридатна конфігурація фільтра\n");
        return;
    }

    puts("=== Траса одного треку ===");
    puts(" k | час, мс | P[k]  | S[k]  | вікно | голоси | вихід");

    for (unsigned k = 0; k < ticks; ++k) {
        const uint32_t now_ms = k * TICK_MS;
        const bool active = confidence_filter_update(&filter, probs[k], now_ms);

        char window[CONFIDENCE_WINDOW_MAX + 1];
        format_window(confidence_filter_window(&filter), FILTER_CFG.window_size, window);

        printf("%2u | %7u | %.3f | %.3f | %s | %u з %u  | %s\n",
               k + 1U, now_ms, (double)probs[k],
               (double)confidence_filter_score(&filter),
               window, confidence_filter_votes(&filter),
               (unsigned)FILTER_CFG.window_size,
               active ? "ТРИВОГА" : "норма");
    }
    puts("");
}

/* Той самий фільтр, але вхід — сирі логіти мережі: калібратор усередині. */
static void demo_calibration(void) {
    static const float logits[][2] = {
        {  6.0f, -1.0f },  /* впевнена детекція */
        {  0.4f,  0.1f },  /* межа видимості */
        { -3.0f,  2.5f },  /* чистий фон */
        { 40.0f, -40.0f }, /* насичений логіт: без зсуву на максимум expf дав би +inf */
    };

    puts("=== Температурне калібрування (T = 2.0) ===");
    for (unsigned i = 0; i < sizeof logits / sizeof logits[0]; ++i) {
        const float raw = confidence_calibrate(logits[i][0], logits[i][1], 1.0f);
        const float cal = confidence_calibrate(logits[i][0], logits[i][1], FILTER_CFG.temperature);
        printf("z = (%+6.1f, %+6.1f)  ->  P(T=1) = %.4f   P(T=2) = %.4f\n",
               (double)logits[i][0], (double)logits[i][1], (double)raw, (double)cal);
    }
    puts("");
}

/* Кадр супроводу: -1 означає, що трекер цього об'єкта в кадрі не побачив. */
typedef struct {
    int         id;
    const char *label;
    float       probs[12];
} TrackScript;

static void demo_pool(void) {
    static const TrackScript scripts[] = {
        { 7,  "пішохід",
          { 0.10f, 0.80f, 0.86f, 0.91f, 0.88f, 0.93f, 0.10f, 0.90f, 0.87f, 0.05f, 0.03f, 0.02f } },
        { 11, "стовп на узбіччі",
          { 0.90f, 0.92f, 0.88f, -1.0f, -1.0f, -1.0f, -1.0f, -1.0f, -1.0f, -1.0f, -1.0f, -1.0f } },
        { 42, "відблиск на асфальті",
          { 0.02f, 0.97f, 0.03f, 0.01f, 0.95f, 0.04f, 0.02f, 0.01f, 0.03f, 0.02f, 0.01f, 0.00f } },
    };
    const unsigned tracks = (unsigned)(sizeof scripts / sizeof scripts[0]);
    const unsigned ticks = 12U;
    const uint32_t track_timeout_ms = 300U;

    TrackerFilterPool pool;
    tracker_pool_init(&pool);

    puts("=== Пул треків (таймаут треку 300 мс) ===");
    for (unsigned k = 0; k < ticks; ++k) {
        const uint32_t now_ms = k * TICK_MS;

        for (unsigned t = 0; t < tracks; ++t) {
            const float p = scripts[t].probs[k];
            if (p < 0.0f) {
                continue; /* Об'єкта в цьому кадрі немає — слот доживає до таймауту. */
            }
            ConfidenceFilter *f = tracker_pool_track(&pool, scripts[t].id, &FILTER_CFG, now_ms);
            if (f == NULL) {
                fprintf(stderr, "Пул вичерпано: трек %d втрачено\n", scripts[t].id);
                continue;
            }
            confidence_filter_update(f, p, now_ms);
        }

        const unsigned dropped = tracker_pool_sweep(&pool, track_timeout_ms, now_ms);

        printf("t = %4u мс | слотів %u | команда: %-9s |",
               now_ms, tracker_pool_size(&pool),
               tracker_pool_any_active(&pool) ? "ГАЛЬМУВАТИ" : "рух");
        for (unsigned t = 0; t < tracks; ++t) {
            const int slot = tracker_pool_find(&pool, scripts[t].id);
            if (slot < 0) {
                continue;
            }
            printf(" %d:%s(%.2f)", scripts[t].id,
                   confidence_filter_active(&pool.filters[slot]) ? "!" : "-",
                   (double)confidence_filter_score(&pool.filters[slot]));
        }
        if (dropped > 0U) {
            printf("  [прибрано за таймаутом: %u]", dropped);
        }
        puts("");
    }

    for (unsigned t = 0; t < tracks; ++t) {
        const int slot = tracker_pool_find(&pool, scripts[t].id);
        printf("трек %2d (%s): %s\n", scripts[t].id, scripts[t].label,
               slot < 0 ? "прибрано за таймаутом"
                        : (confidence_filter_active(&pool.filters[slot]) ? "тривога" : "норма"));
    }
    puts("");
}

/* Пул скінченний, і переповнення — не гіпотеза: у щільному потоці трекер
 * легко видає більше рамок, ніж є слотів. */
static void demo_pool_exhaustion(void) {
    TrackerFilterPool pool;
    tracker_pool_init(&pool);

    puts("=== Переповнення пулу ===");
    for (int id = 100; id < 100 + MAX_TRACKED_OBJECTS; ++id) {
        if (tracker_pool_track(&pool, id, &FILTER_CFG, 0U) == NULL) {
            printf("несподівана відмова на треку %d\n", id);
            return;
        }
    }
    printf("зайнято слотів: %u з %d\n", tracker_pool_size(&pool), MAX_TRACKED_OBJECTS);

    if (tracker_pool_track(&pool, 999, &FILTER_CFG, 0U) == NULL) {
        puts("трек 999 відхилено — пул вичерпано (виклик мусить це помітити)");
    }

    tracker_pool_release(&pool, 100);
    if (tracker_pool_track(&pool, 999, &FILTER_CFG, 0U) != NULL) {
        puts("після звільнення слоту трек 999 прийнято");
    }
    puts("");
}

int main(void) {
    if (!confidence_config_valid(&FILTER_CFG)) {
        fprintf(stderr, "Конфігурація не пройшла перевірку\n");
        return 1;
    }
    demo_calibration();
    demo_trace();
    demo_pool();
    demo_pool_exhaustion();
    return 0;
}
