#include <stddef.h>
#include <stdio.h>

#include "loading.h"
#include "report.h"

/* Стенд із розділу: дільник 5.00 В на двох резисторах 1.00 МОм,
   виміряний трьома приладами різного класу, і шина живлення
   з прецизійним шунтом 1.00 Ом у розриві. */

struct meter {
    const char *name;
    double r_meter;
};

static const struct meter METERS[] = {
    { "кишеньковий мультиметр",   1.0e6  },
    { "лабораторний мультиметр",  10.0e6 },
    { "буфер на польовому вході", 10.0e9 }
};

#define METER_COUNT (sizeof METERS / sizeof METERS[0])
#define LAB_METER   1  /* саме показ лабораторного приладу піде в протокол */

/* Проходить дільник трьома приладами; повертає показ лабораторного
   мультиметра та відновлену з нього напругу холостого ходу. */
static int survey_divider(thevenin_t *node, double *lab_reading, double *lab_restored)
{
    size_t i;
    calc_err_t err = thevenin_of_divider(5.00, 1.0e6, 1.0e6, node);

    if (err != CALC_OK) {
        fprintf(stderr, "дільник: %s\n", calc_err_text(err));
        return -1;
    }

    printf("Вузол дільника: U_th = %.5f В, R_th = %.0f Ом\n\n", node->u_th, node->r_th);

    for (i = 0; i < METER_COUNT; ++i) {
        loading_t direct;
        loading_t restored;

        err = voltmeter_reading(node, METERS[i].r_meter, &direct);
        if (err != CALC_OK) {
            fprintf(stderr, "%s: %s\n", METERS[i].name, calc_err_text(err));
            return -1;
        }

        /* Обернений хід: за самим лише показом приладу відновлюємо U_th —
           це і є та корекція, яку роблять руками над журналом. */
        err = correct_loading(direct.u_meas, node->r_th, METERS[i].r_meter, &restored);
        if (err != CALC_OK) {
            fprintf(stderr, "%s: %s\n", METERS[i].name, calc_err_text(err));
            return -1;
        }

        report_put_left(METERS[i].name, 26);
        printf("R_m = %8.3g МОм   показ %.4f В   δ = %+6.2f %%   R_m/R_th = %8.1f   %s\n",
               METERS[i].r_meter / 1.0e6,
               direct.u_meas,
               direct.error_pct,
               direct.ratio,
               verdict_text(direct.verdict));
        printf("%26s  відновлена U_th = %.5f В\n", "", restored.u_true);

        if (i == LAB_METER) {
            *lab_reading = direct.u_meas;
            *lab_restored = restored.u_true;
        }
    }
    return 0;
}

/* Оцінює просідання шини живлення до виводу чипа й опір контактів. */
static int survey_rail(contact_t *est)
{
    const double u_supply = 5.000;   /* виставлено на блоці живлення */
    const double u_shunt  = 0.0475;  /* мілівольтметр на шунті 1.00 Ом */
    const double u_pin    = 4.886;   /* виміряно просто на виводі V_CC чипа */
    const double r_shunt  = 1.00;
    const int contacts    = 4;       /* дві клеми макетки плюс дві перемички */

    calc_err_t err = estimate_contact_resistance(u_supply, u_shunt, u_pin,
                                                 r_shunt, contacts, est);
    if (err != CALC_OK) {
        fprintf(stderr, "шина живлення: %s\n", calc_err_text(err));
        return -1;
    }

    printf("\nСтрум гілки за шунтом:    %8.2f мА\n", est->i_branch * 1000.0);
    printf("Просідання шини до чипа:  %8.1f мВ\n", est->u_drop * 1000.0);
    printf("Опір шляху живлення:      %8.3f Ом на %d контакти\n", est->r_path, contacts);
    printf("Опір одного контакту:     %8.3f Ом   %s\n\n",
           est->r_per_contact, verdict_text(est->verdict));
    return 0;
}

int main(void)
{
    thevenin_t node;
    contact_t rail;
    dc_row_t rows[4];
    verdict_t overall;
    double lab_reading = 0.0;
    double lab_restored = 0.0;

    if (survey_divider(&node, &lab_reading, &lab_restored) != 0) {
        return 1;
    }
    if (survey_rail(&rail) != 0) {
        return 1;
    }

    rows[0].name = "Живлення на виводі V_CC чипа";
    rows[0].unit = "В";
    rows[0].calc = 5.000;
    rows[0].meas = 4.886;
    rows[0].tol_pct = 2.0;

    rows[1].name = "Середня точка, сирий показ 10 МОм";
    rows[1].unit = "В";
    rows[1].calc = node.u_th;
    rows[1].meas = lab_reading;
    rows[1].tol_pct = 1.0;

    rows[2].name = "Середня точка після корекції";
    rows[2].unit = "В";
    rows[2].calc = node.u_th;
    rows[2].meas = lab_restored;
    rows[2].tol_pct = 1.0;

    rows[3].name = "Струм гілки за шунтом";
    rows[3].unit = "мА";
    rows[3].calc = 45.0;
    rows[3].meas = rail.i_branch * 1000.0;
    rows[3].tol_pct = 10.0;

    dc_table_print(rows, sizeof rows / sizeof rows[0]);

    overall = dc_table_verdict(rows, sizeof rows / sizeof rows[0]);
    if (rail.verdict > overall) {
        overall = rail.verdict;
    }
    printf("\nЗагальний вердикт вузла: %s\n", verdict_text(overall));

    /* Ненульовий код повернення дає скриптові стенда підставу зупинити прогін. */
    return (overall == V_FAIL) ? 1 : 0;
}
