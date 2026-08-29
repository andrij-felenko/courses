/* Калькулятор автономності польового вузла.
 *
 * Дані комірки взяті з даташиту літій-тіонілхлоридного елемента розміру A
 * (2400 мА·год, плато 3.6 В), профіль споживання — з осцилограми реальної
 * плати LoRaWAN. П'ять сценаріїв показують, як та сама плата з тією самою
 * батареєю живе від чотирьох місяців до дванадцяти років — і в якому
 * випадку вона не переживе навіть першої передачі.
 */

#include "battery.h"
#include "dutycycle.h"
#include "lifetime.h"

#include <stdio.h>

/* ---------- даташит комірки ---------- */

/* Розрядна крива Li-SOCl2: майже все віддається на плато 3.5–3.6 В, тому
 * кожні сто мілівольт порогу відсічки коштують дуже дорого. */
static const bat_curve_point ls_curve[] = {
    { 3.67, 0.00 }, { 3.62, 0.02 }, { 3.58, 0.20 }, { 3.55, 0.45 },
    { 3.52, 0.70 }, { 3.48, 0.85 }, { 3.40, 0.93 }, { 3.20, 0.97 },
    { 2.80, 0.99 }, { 2.00, 1.00 }
};

static const bat_temp_point ls_temp[] = {
    { -40.0, 0.30 }, { -20.0, 0.60 }, { 0.0, 0.85 },
    {  20.0, 1.00 }, {  40.0, 1.00 }, { 60.0, 0.95 }
};

static const battery_t li_socl2 = {
    .name                   = "Li-SOCl2, розмір A",
    .capacity_mah           = 2400.0,
    .ocv_fresh_v            = 3.67,
    .reference_current_ma   = 1.0,    /* паспортну ємність міряли струмом 1 мА */
    .r_int_20c_ohm          = 0.50,
    .r_int_beta_k           = 6300.0, /* дає ≈15 Ом за −20 °C */
    .peukert_k              = 1.08,
    .relax_time_s           = 30.0,
    .self_discharge_pct_year = 1.5,
    .passivation_max_factor = 200.0,  /* зріла плівка LiCl — сотні ом */
    .passivation_onset_days = 730.0,
    .curve                  = ls_curve,
    .curve_len              = sizeof ls_curve / sizeof ls_curve[0],
    .temp_curve             = ls_temp,
    .temp_len               = sizeof ls_temp / sizeof ls_temp[0]
};

/* ---------- профілі споживання ---------- */

static const dc_phase lora_phases[] = {
    { "Пробудження й вимірювання",  8.0,  50.0 },
    { "Передача LoRa SF10",        45.0, 150.0 },
    { "Запис лічильника в EEPROM",  4.0,  10.0 }
};

static const dc_phase nbiot_phases[] = {
    { "Пробудження й вимірювання", 12.0,   80.0 },
    { "Реєстрація й сеанс NB-IoT", 250.0, 1800.0 },
    { "Запис лічильника в EEPROM",  4.0,   10.0 }
};

typedef struct {
    const char *title;
    duty_cycle_t duty;
    site_t site;
} scenario_t;

static const scenario_t scenarios[] = {
    {
        "Кімнатна температура, передача щохвилини",
        { lora_phases, 3, 0.005, 60.0,
          { "Депасиваційний імпульс", 8.0, 30.0 }, 86400.0 },
        { 2.90, 20.0, 30.0, 0.80 }
    },
    {
        "Мороз −20 °C, той самий вузол і той самий цикл",
        { lora_phases, 3, 0.005, 60.0,
          { "Депасиваційний імпульс", 8.0, 30.0 }, 86400.0 },
        { 2.90, -20.0, 30.0, 0.80 }
    },
    {
        "Ящик на сонці +50 °C, передача раз на 10 хвилин",
        { lora_phases, 3, 0.005, 600.0,
          { "Депасиваційний імпульс", 8.0, 30.0 }, 86400.0 },
        { 2.90, 50.0, 30.0, 0.80 }
    },
    {
        "Два роки на складі: перший імпульс після пасивації",
        { lora_phases, 3, 0.005, 600.0,
          { "Депасиваційний імпульс", 0.0, 0.0 }, 0.0 },
        { 2.90, 20.0, 730.0, 0.80 }
    },
    {
        "NB-IoT на морозі: 250 мА в пік, поріг модема 3.1 В",
        { nbiot_phases, 3, 0.008, 900.0,
          { "Депасиваційний імпульс", 0.0, 0.0 }, 0.0 },
        { 3.10, -20.0, 30.0, 0.80 }
    }
};

/* ---------- друк звіту ---------- */

/* printf вирівнює за байтами, а кирилиця в UTF-8 займає по два байти на
 * літеру — без власного відступу таблиця розповзається. */
static int glyphs_of(const char *text)
{
    const unsigned char *p;
    int glyphs = 0;

    /* продовження багатобайтової послідовності має старші біти 10 */
    for (p = (const unsigned char *)text; *p; ++p)
        if ((*p & 0xC0) != 0x80)
            ++glyphs;
    return glyphs;
}

static void pad(const char *text, int width)
{
    int glyphs = glyphs_of(text);

    fputs(text, stdout);
    while (glyphs++ < width)
        putchar(' ');
}

static void padr(const char *text, int width)
{
    int glyphs = glyphs_of(text);

    while (glyphs++ < width)
        putchar(' ');
    fputs(text, stdout);
}

static void rule(char c)
{
    int i;
    for (i = 0; i < 74; ++i)
        putchar(c);
    putchar('\n');
}

static void print_waterfall(const battery_t *b, const site_t *s, const estimate_t *e)
{
    puts("ВОДОСПАД ЄМНОСТІ");
    pad("  паспортна ємність", 46);
    printf("%9.1f мА·год\n", b->capacity_mah);

    printf("  × η_cutoff = %.3f (поріг %.2f В + просадка %.2f В)\n",
           e->eta_cutoff, s->cutoff_v, e->pulse.sag_v);
    pad("    доступно за напругою", 46);
    printf("%9.1f мА·год\n", e->c_after_cutoff_mah);

    printf("  × η_temp   = %.3f (%+.0f °C)\n", e->eta_temp, s->temp_c);
    pad("    доступно за температурою", 46);
    printf("%9.1f мА·год\n", e->c_after_temp_mah);

    printf("  × η_pulse  = %.3f (пік %.1f мА, спокій %.0f с)\n",
           e->eta_pulse, e->duty.peak_current_ma, e->duty.rest_s);
    pad("  ФАКТИЧНО ДОСТУПНО", 46);
    printf("%9.1f мА·год  (%.1f %% паспорта)\n",
           e->c_eff_mah, 100.0 * e->c_eff_mah / b->capacity_mah);
}

static void print_row(const dc_phase_result *r)
{
    pad("  ", 2);
    pad(r->name, 30);
    printf("%9.3f %9.1f %10.3f %8.1f %%  ×%.3f\n",
           r->current_ma, r->duration_ms, r->charge_mas,
           100.0 * r->share, r->peukert_cost);
}

static void print_phases(const duty_result_t *d, const site_t *s)
{
    size_t i;

    printf("ЗАРЯД ЗА ЦИКЛ (період %.0f с, температура %+.0f °C)\n",
           d->active_s + d->rest_s, s->temp_c);
    pad("  фаза", 32);
    padr("I, мА", 9);
    padr("t, мс", 10);
    padr("Q, мА·с", 11);
    padr("частка", 9);
    fputs("    ", stdout);
    fputs("Пейкерт\n", stdout);

    for (i = 0; i < d->count; ++i)
        print_row(&d->per_phase[i]);
    print_row(&d->sleep);
    if (d->has_depass)
        print_row(&d->depass);

    pad("  разом за цикл", 32);
    printf("%9s %9s %10.3f %8.1f %%\n", "", "", d->q_cycle_mas, 100.0);
}

static void print_currents(const battery_t *b, const site_t *s, const estimate_t *e)
{
    puts("СТРУМИ");
    pad("  середній струм навантаження", 46);
    printf("%9.2f мкА\n", e->i_avg_ma * 1000.0);
    pad("  еквівалентний струм саморозряду", 46);
    printf("%9.2f мкА  (%.2f %%/рік за %+.0f °C)\n",
           e->i_self_ma * 1000.0,
           100.0 * e->i_self_ma * 8766.0 / b->capacity_mah,
           s->temp_c);
    pad("  разом", 46);
    printf("%9.2f мкА\n", e->i_total_ma * 1000.0);
}

static void print_pulse(const site_t *s, const estimate_t *e)
{
    const pulse_report_t *p = &e->pulse;

    puts("ІМПУЛЬС ПЕРЕДАВАЧА");
    printf("  внутрішній опір за %+.0f °C: %.2f Ом\n", s->temp_c, p->r_int_ohm);
    printf("  просадка %.1f мА · %.2f Ом = %.2f В → на клемах %.2f В (поріг %.2f В)  %s\n",
           e->duty.peak_current_ma, p->r_int_ohm, p->sag_v, p->v_term_v, s->cutoff_v,
           p->brownout ? "✖ СКИДАННЯ" : "гаразд");
    printf("  після %.0f діб спокою опір %.1f Ом → на клемах %.2f В  %s\n",
           s->storage_days, p->r_passivated_ohm, p->v_term_storage_v,
           p->brownout_after_storage ? "✖ СКИДАННЯ" : "гаразд");

    if (!p->buffer_needed) {
        puts("  буфер не потрібен: імпульс укладається в бюджет напруги");
        return;
    }
    if (p->buffer_impossible) {
        puts("  ✖ поріг відсічки вищий за робоче плато комірки — буфер не врятує,");
        puts("    треба інша хімія, нижчий поріг або менший піковий струм");
        return;
    }
    printf("  потрібен буфер ≥ %.0f мкФ з ESR ≤ %.2f Ом (запас %.2f В)\n",
           p->buffer_farads * 1.0e6, p->buffer_esr_max_ohm, p->headroom_v);
    puts(p->buffer_farads > 1.0e-3
         ? "  керамікою й танталом стільки не набрати — потрібен гібридний шар (HLC)"
         : "  вистачить банку танталових конденсаторів із низьким ESR");
}

static void print_lifetime(const site_t *s, const estimate_t *e)
{
    puts("ЧАС АВТОНОМНОСТІ");
    pad("  наївна оцінка (паспорт / I_avg)", 46);
    printf("%9.2f року\n", e->naive_years);

    if (e->c_eff_mah <= 0.0 || e->years <= 0.0) {
        puts("  реальна оцінка                                    0 — пристрій не працює");
    } else {
        pad("  реальна оцінка", 46);
        printf("%9.2f року  (%.0f діб, %.0f год)\n", e->years, e->days, e->hours);
        pad("  з інженерним запасом", 46);
        printf("%9.2f року  (k_safe = %.2f)\n", e->guaranteed_years, s->safety_factor);
        printf("  наївний розрахунок завищений у %.1f раза\n", e->optimism_ratio);
    }

    printf("  обмежувач: %s — %s\n", limiter_str(e->limiter), e->limiter_note);
}

static void run(const scenario_t *sc)
{
    estimate_t est;
    est_status st;

    rule('=');
    printf("СЦЕНАРІЙ: %s\n", sc->title);
    printf("Комірка: %s, %.0f мА·год · відсічка %.2f В · запас %.2f\n",
           li_socl2.name, li_socl2.capacity_mah, sc->site.cutoff_v, sc->site.safety_factor);
    rule('-');

    st = lifetime_estimate(&li_socl2, &sc->duty, &sc->site, &est);
    if (st != EST_OK) {
        printf("✖ розрахунок неможливий: %s\n", est_status_str(st));
        return;
    }

    print_waterfall(&li_socl2, &sc->site, &est);
    rule('-');
    print_phases(&est.duty, &sc->site);
    rule('-');
    print_currents(&li_socl2, &sc->site, &est);
    rule('-');
    print_pulse(&sc->site, &est);
    rule('-');
    print_lifetime(&sc->site, &est);
    putchar('\n');
}

int main(void)
{
    size_t i;

    for (i = 0; i < sizeof scenarios / sizeof scenarios[0]; ++i)
        run(&scenarios[i]);

    return 0;
}
