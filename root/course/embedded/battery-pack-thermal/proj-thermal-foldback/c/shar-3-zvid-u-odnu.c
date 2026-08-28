#include <stdbool.h>

#define N_SENSORS    4              // давачів у пакеті
#define T_PLAUSIBLE_LO  (-300)      // −30.0 °C: холодніше — давач бреше
#define T_PLAUSIBLE_HI   (800)      // +80.0 °C: гарячіше — або втеча, або брехня

// Один давач: код АЦП → температура з повною перевіркою справності.
// valid=false означає «цьому давачу вірити не можна».
typedef struct { int16_t t_c10; bool valid; } reading_t;

reading_t read_sensor(uint16_t adc_code) {
    reading_t r = { .t_c10 = 0, .valid = false };

    int32_t ohm = adc_to_ohm(adc_code);
    if (ohm <= 0) return r;                       // обрив або КЗ давача

    int16_t t = ohm_to_c10(ohm);
    if (t == INT16_MIN) return r;                 // поза таблицею

    if (t < T_PLAUSIBLE_LO || t > T_PLAUSIBLE_HI) // фізично неможливо
        return r;

    r.t_c10 = t;
    r.valid = true;
    return r;
}

// Звід кількох давачів: максимум серед СПРАВНИХ. Окремо повертаємо,
// скільки давачів живі — за цим машина станів вирішить, чи можна довіряти пакету.
typedef struct { int16_t t_max_c10; int n_valid; } pack_temp_t;

pack_temp_t pack_temperature(const uint16_t *codes) {
    pack_temp_t out = { .t_max_c10 = INT16_MIN, .n_valid = 0 };
    for (int i = 0; i < N_SENSORS; i++) {
        reading_t r = read_sensor(codes[i]);
        if (!r.valid) continue;
        out.n_valid++;
        if (r.t_c10 > out.t_max_c10)
            out.t_max_c10 = r.t_c10;
    }
    return out;
}
