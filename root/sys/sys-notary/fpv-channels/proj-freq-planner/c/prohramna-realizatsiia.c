#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#define MAX_CHANNELS 48
#define MAX_PILOTS   8

typedef struct {
    const char *band_name;
    int channel_num;
    int freq_mhz;
} FpvChannel;

/* Стандартна таблиця 48 каналів 5.8 ГГц */
static const FpvChannel ALL_CHANNELS[MAX_CHANNELS] = {
    /* Band A (Boscam A) */
    {"A", 1, 5865}, {"A", 2, 5845}, {"A", 3, 5825}, {"A", 4, 5805},
    {"A", 5, 5785}, {"A", 6, 5765}, {"A", 7, 5745}, {"A", 8, 5725},
    /* Band B (Boscam B) */
    {"B", 1, 5733}, {"B", 2, 5752}, {"B", 3, 5771}, {"B", 4, 5790},
    {"B", 5, 5809}, {"B", 6, 5828}, {"B", 7, 5847}, {"B", 8, 5866},
    /* Band E (Foxtech) */
    {"E", 1, 5705}, {"E", 2, 5685}, {"E", 3, 5665}, {"E", 4, 5645},
    {"E", 5, 5885}, {"E", 6, 5905}, {"E", 7, 5925}, {"E", 8, 5945},
    /* Band F (FatShark) */
    {"F", 1, 5740}, {"F", 2, 5760}, {"F", 3, 5780}, {"F", 4, 5800},
    {"F", 5, 5820}, {"F", 6, 5840}, {"F", 7, 5860}, {"F", 8, 5880},
    /* Band R (Raceband) */
    {"R", 1, 5658}, {"R", 2, 5695}, {"R", 3, 5732}, {"R", 4, 5769},
    {"R", 5, 5806}, {"R", 6, 5843}, {"R", 7, 5880}, {"R", 8, 5917},
    /* Band L (Lowband) */
    {"L", 1, 5362}, {"L", 2, 5399}, {"L", 3, 5436}, {"L", 4, 5473},
    {"L", 5, 5510}, {"L", 6, 5547}, {"L", 7, 5584}, {"L", 8, 5621}
};

typedef struct {
    int pilot_count;
    int freqs[MAX_PILOTS];
    char labels[MAX_PILOTS][32];
} FrequencyPlan;

typedef struct {
    int direct_conflicts;
    int adjacent_conflicts;
    int imd3_two_tone_conflicts;
    int imd3_three_tone_conflicts;
    int min_spacing_mhz;
} ConflictReport;

/* Перевірка набору частот на наявність колізій */
ConflictReport analyze_plan(const FrequencyPlan *plan, int min_adj_mhz, int imd_guard_mhz, bool verbose) {
    ConflictReport report = {0, 0, 0, 0, 9999};
    int n = plan->pilot_count;

    /* 1. Перевірка сусідніх та прямих каналів */
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            int diff = abs(plan->freqs[i] - plan->freqs[j]);
            if (diff < report.min_spacing_mhz) {
                report.min_spacing_mhz = diff;
            }
            if (diff == 0) {
                report.direct_conflicts++;
                if (verbose) {
                    printf("  [КОЛІЗІЯ] Прямий збіг: %s та %s (%d МГц)\n",
                           plan->labels[i], plan->labels[j], plan->freqs[i]);
                }
            } else if (diff < min_adj_mhz) {
                report.adjacent_conflicts++;
                if (verbose) {
                    printf("  [УВАГА] Недостатній інтервал: %s та %s (Δf = %d МГц < %d МГц)\n",
                           plan->labels[i], plan->labels[j], diff, min_adj_mhz);
                }
            }
        }
    }

    /* 2. Перевірка двотонового IMD3: 2*f1 - f2 */
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            if (i == j) continue;
            int f_imd = 2 * plan->freqs[i] - plan->freqs[j];
            for (int k = 0; k < n; ++k) {
                if (k == i || k == j) continue;
                int diff = abs(f_imd - plan->freqs[k]);
                if (diff < imd_guard_mhz) {
                    report.imd3_two_tone_conflicts++;
                    if (verbose) {
                        printf("  [IMD3 2-Tone] 2·%s − %s = %d МГц б'є в %s (%d МГц), похибка %d МГц\n",
                               plan->labels[i], plan->labels[j], f_imd,
                               plan->labels[k], plan->freqs[k], diff);
                    }
                }
            }
        }
    }

    /* 3. Перевірка тритонового IMD3: f1 + f2 - f3 */
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            for (int k = 0; k < n; ++k) {
                if (k == i || k == j) continue;
                int f_triple = plan->freqs[i] + plan->freqs[j] - plan->freqs[k];
                for (int m = 0; m < n; ++m) {
                    if (m == i || m == j || m == k) continue;
                    int diff = abs(f_triple - plan->freqs[m]);
                    if (diff < imd_guard_mhz) {
                        report.imd3_three_tone_conflicts++;
                        if (verbose) {
                            printf("  [IMD3 3-Tone] %s + %s − %s = %d МГц б'є в %s (%d МГц), похибка %d МГц\n",
                                   plan->labels[i], plan->labels[j], plan->labels[k],
                                   f_triple, plan->labels[m], plan->freqs[m], diff);
                        }
                    }
                }
            }
        }
    }

    return report;
}

int main(void) {
    printf("=== АНАЛІЗ ЧАСТОТНИХ ПЛАНІВ ДЛЯ FPV 5.8 ГГц ===\n\n");

    /* Тест 1: Класична небезпечна сітка Band F (F1, F2, F3, F4) */
    FrequencyPlan bad_plan;
    bad_plan.pilot_count = 4;
    bad_plan.freqs[0] = 5740; strcpy(bad_plan.labels[0], "F1 (5740)");
    bad_plan.freqs[1] = 5760; strcpy(bad_plan.labels[1], "F2 (5760)");
    bad_plan.freqs[2] = 5780; strcpy(bad_plan.labels[2], "F3 (5780)");
    bad_plan.freqs[3] = 5800; strcpy(bad_plan.labels[3], "F4 (5800)");

    printf("1. Аналіз небезпечної сітки Band F (крок 20 МГц):\n");
    ConflictReport r1 = analyze_plan(&bad_plan, 25, 10, true);
    printf("Результат: Конфліктів сусідніх: %d, IMD3 2-тонових: %d, Тритонових: %d\n\n",
           r1.adjacent_conflicts, r1.imd3_two_tone_conflicts, r1.imd3_three_tone_conflicts);

    /* Тест 2: Оптимізована сітка Raceband (R1, R2, R4, R7) */
    FrequencyPlan race_plan;
    race_plan.pilot_count = 4;
    race_plan.freqs[0] = 5658; strcpy(race_plan.labels[0], "R1 (5658)");
    race_plan.freqs[1] = 5695; strcpy(race_plan.labels[1], "R2 (5695)");
    race_plan.freqs[2] = 5769; strcpy(race_plan.labels[2], "R4 (5769)");
    race_plan.freqs[3] = 5880; strcpy(race_plan.labels[3], "R7 (5880)");

    printf("2. Аналіз оптимізованої сітки Raceband (R1, R2, R4, R7):\n");
    ConflictReport r2 = analyze_plan(&race_plan, 25, 10, true);
    printf("Результат: Конфліктів сусідніх: %d, IMD3 2-тонових: %d, Тритонових: %d\n",
           r2.adjacent_conflicts, r2.imd3_two_tone_conflicts, r2.imd3_three_tone_conflicts);
    printf("Мінімальний інтервал між пілотами: %d МГц\n", r2.min_spacing_mhz);

    return 0;
}
