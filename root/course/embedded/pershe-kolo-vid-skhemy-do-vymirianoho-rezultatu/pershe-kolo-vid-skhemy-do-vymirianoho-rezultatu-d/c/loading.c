#include "loading.h"

#include <math.h>
#include <stddef.h>

const char *calc_err_text(calc_err_t err)
{
    switch (err) {
    case CALC_OK:             return "гаразд";
    case CALC_BAD_ARG:        return "некоректний аргумент";
    case CALC_BAD_RESISTANCE: return "опір мусить бути додатним";
    case CALC_BAD_CURRENT:    return "струм замалий для оцінки опору";
    case CALC_BAD_DROP:       return "напруга на виводі вища за напругу джерела";
    }
    return "невідома помилка";
}

const char *verdict_text(verdict_t v)
{
    switch (v) {
    case V_PASS: return "PASS";
    case V_WARN: return "WARN";
    case V_FAIL: return "FAIL";
    }
    return "????";
}

calc_err_t thevenin_of_divider(double u_supply, double r_top, double r_bottom,
                               thevenin_t *out)
{
    if (out == NULL) {
        return CALC_BAD_ARG;
    }
    if (r_top <= 0.0 || r_bottom <= 0.0) {
        return CALC_BAD_RESISTANCE;
    }
    out->u_th = u_supply * r_bottom / (r_top + r_bottom);
    /* Вихідний опір — паралельне з'єднання плечей: джерело живлення
       для змінної складової є коротким замиканням на землю. */
    out->r_th = (r_top * r_bottom) / (r_top + r_bottom);
    return CALC_OK;
}

/* «Золоте правило»: щоб похибка навантаження не вийшла за 1 %,
   вхідний опір приладу мусить бути стократ вищий за R_th вузла. */
static verdict_t rule_of_hundred(double ratio)
{
    if (ratio >= 100.0) {
        return V_PASS;
    }
    if (ratio >= 10.0) {
        return V_WARN;
    }
    return V_FAIL;
}

static void fill_loading(loading_t *out, double u_true, double u_meas,
                         double r_th, double r_meter)
{
    out->u_true = u_true;
    out->u_meas = u_meas;
    /* Ідеальний вузол (R_th = 0) прилад не навантажує взагалі. */
    out->error_pct = (fabs(u_true) < 1e-12)
                     ? 0.0
                     : (u_meas - u_true) / u_true * 100.0;
    out->ratio = (r_th <= 0.0) ? INFINITY : r_meter / r_th;
    out->verdict = rule_of_hundred(out->ratio);
}

calc_err_t voltmeter_reading(const thevenin_t *node, double r_meter, loading_t *out)
{
    double u_meas;

    if (node == NULL || out == NULL) {
        return CALC_BAD_ARG;
    }
    if (r_meter <= 0.0 || node->r_th < 0.0) {
        return CALC_BAD_RESISTANCE;
    }
    /* Прилад стає нижнім плечем дільника: U = U_th / (1 + R_th/R_m). */
    u_meas = node->u_th / (1.0 + node->r_th / r_meter);
    fill_loading(out, node->u_th, u_meas, node->r_th, r_meter);
    return CALC_OK;
}

calc_err_t correct_loading(double u_meas, double r_th, double r_meter, loading_t *out)
{
    double u_true;

    if (out == NULL) {
        return CALC_BAD_ARG;
    }
    if (r_meter <= 0.0 || r_th < 0.0) {
        return CALC_BAD_RESISTANCE;
    }
    /* Те саме рівняння, розв'язане відносно напруги холостого ходу. */
    u_true = u_meas * (1.0 + r_th / r_meter);
    fill_loading(out, u_true, u_meas, r_th, r_meter);
    return CALC_OK;
}

calc_err_t shunt_current(double u_shunt, double r_shunt, double *i_out)
{
    if (i_out == NULL) {
        return CALC_BAD_ARG;
    }
    if (r_shunt <= 0.0) {
        return CALC_BAD_RESISTANCE;
    }
    *i_out = u_shunt / r_shunt;
    return CALC_OK;
}

calc_err_t estimate_contact_resistance(double u_supply, double u_shunt, double u_pin,
                                       double r_shunt, int contacts, contact_t *out)
{
    calc_err_t err;
    double current;
    double drop;

    if (out == NULL || contacts <= 0) {
        return CALC_BAD_ARG;
    }
    err = shunt_current(u_shunt, r_shunt, &current);
    if (err != CALC_OK) {
        return err;
    }
    /* Нижче мікроампера просідання на контактах тоне в розрядності
       мілівольтметра — рахувати опір з такого ділення не можна. */
    if (current < 1e-6) {
        return CALC_BAD_CURRENT;
    }

    /* Шунт стоїть у розриві шини, тож його падіння віднімаємо окремо:
       решта втрати припадає на клеми макетки й перемички. */
    drop = u_supply - u_shunt - u_pin;
    if (drop < 0.0) {
        return CALC_BAD_DROP;
    }

    out->i_branch = current;
    out->u_drop = drop;
    out->r_path = drop / current;
    out->r_per_contact = out->r_path / (double)contacts;

    /* Норми з тексту розділу: нова плата дає 0.05–0.3 Ом на контакт,
       розхитане чи окиснене гніздо — 0.5 Ом і більше. */
    if (out->r_per_contact <= 0.3) {
        out->verdict = V_PASS;
    } else if (out->r_per_contact <= 0.5) {
        out->verdict = V_WARN;
    } else {
        out->verdict = V_FAIL;
    }
    return CALC_OK;
}
