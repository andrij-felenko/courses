/* szilard_sim.c - Чисельна симуляція двигуна Сіларда мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define KB 1.380649e-23     /* Стала Больцмана, Дж/К */
#define T_ROOM 300.0        /* Кімнатна температура, К */
#define LN2 0.69314718056   /* Натуральний логарифм 2 */

typedef enum {
    POS_LEFT = 0,
    POS_RIGHT = 1
} MoleculePos;

typedef struct {
    double total_work_extracted; /* Сумарна вилучена робота, Дж */
    double total_heat_absorbed;  /* Тепло, поглинуте при розширенні, Дж */
    double total_heat_erased;    /* Тепло, виділене при стиранні, Дж */
    double net_entropy_change;   /* Сумарна зміна ентропії, Дж/К */
    unsigned long cycles;        /* Кількість виконаних циклів */
} ThermoStats;

/* Ініціалізація статистики */
void stats_init(ThermoStats *st) {
    st->total_work_extracted = 0.0;
    st->total_heat_absorbed = 0.0;
    st->total_heat_erased = 0.0;
    st->net_entropy_change = 0.0;
    st->cycles = 0;
}

/* Симуляція одного циклу Сіларда */
void run_szilard_cycle(ThermoStats *st, double temp) {
    /* Крок 1: Випадкове положення молекули (L або R) */
    MoleculePos mol_actual = (rand() % 2 == 0) ? POS_LEFT : POS_RIGHT;

    /* Крок 2: Вимірювання демоном (запис 1 біта) */
    int memory_bit = (mol_actual == POS_LEFT) ? 0 : 1;

    /* Крок 3: Ізотермічне розширення та вилучення роботи */
    double work = KB * temp * LN2;
    double q_in = work;

    /* Крок 4: Стирання пам'яті за Ландауером (скидання memory_bit -> 0) */
    /* Моделюємо реальне стирання з мінімальною межею Ландауера */
    double q_erasure = KB * temp * LN2;
    double ds_bath = - q_in / temp;        /* Зменшення ентропії при розширенні */
    double ds_erasure = q_erasure / temp;  /* Зростання ентропії при стиранні */

    /* Крок 5: Накопичення статистики */
    st->total_work_extracted += work;
    st->total_heat_absorbed += q_in;
    st->total_heat_erased += q_erasure;
    st->net_entropy_change += (ds_bath + ds_erasure);
    st->cycles++;

    (void)memory_bit; /* Запобігання попередженню про невикористану змінну */
}

int main(void) {
    srand((unsigned int)time(NULL));
    ThermoStats stats;
    stats_init(&stats);

    const unsigned long N_CYCLES = 100000;
    printf("=== Симуляція двигуна Сіларда (C) [%lu циклів] ===\n", N_CYCLES);

    for (unsigned long i = 0; i < N_CYCLES; i++) {
        run_szilard_cycle(&stats, T_ROOM);
    }

    double avg_work_eV = (stats.total_work_extracted / N_CYCLES) / 1.602176634e-19;
    double avg_erasure_eV = (stats.total_heat_erased / N_CYCLES) / 1.602176634e-19;
    double avg_ds = stats.net_entropy_change / N_CYCLES;

    printf("Середня вилучена робота за цикл : %.4f meV (теорія: %.4f meV)\n",
           avg_work_eV * 1000.0, (KB * T_ROOM * LN2 / 1.602176634e-19) * 1000.0);
    printf("Середнє виділене тепло стирання : %.4f meV (межа Ландауера: %.4f meV)\n",
           avg_erasure_eV * 1000.0, (KB * T_ROOM * LN2 / 1.602176634e-19) * 1000.0);
    printf("Чиста зміна ентропії за цикл    : %.6e Дж/К (теорія: 0.0)\n", avg_ds);

    return 0;
}
