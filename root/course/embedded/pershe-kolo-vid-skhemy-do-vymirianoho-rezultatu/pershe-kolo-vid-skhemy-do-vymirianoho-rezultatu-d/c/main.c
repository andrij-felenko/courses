#include <stdio.h>
#include <stdbool.h>

typedef struct {
    double v_meas;      /* Виміряна напруга (В) */
    double r_thevenin;  /* Еквівалентний опір вузла схеми (Ом) */
    double r_meter;     /* Вхідний опір вольтметра (Ом) */
    double v_actual;    /* Розрахована істинна напруга холостого ходу (В) */
    double error_pct;   /* Відносна похибка навантаження (%) */
} NodeCorrection_t;

bool correct_voltmeter_loading(double v_meas, double r_thevenin, double r_meter, NodeCorrection_t *out) {
    if (r_meter <= 0.0 || r_thevenin < 0.0 || out == NULL) {
        return false;
    }
    out->v_meas = v_meas;
    out->r_thevenin = r_thevenin;
    out->r_meter = r_meter;
    
    /* Відновлення істинної напруги за формулою Тевеніна */
    out->v_actual = v_meas * (1.0 + (r_thevenin / r_meter));
    out->error_pct = ((v_meas - out->v_actual) / out->v_actual) * 100.0;
    return true;
}

int main(void) {
    NodeCorrection_t res;
    double v_read = 1.6667;
    double r_th = 500000.0; /* 500 кОм */
    double r_m = 1000000.0;  /* 1 МОм мультиметр */

    if (correct_voltmeter_loading(v_read, r_th, r_m, &res)) {
        printf("Показ вольтметра:   %.4f V\n", res.v_meas);
        printf("Істинна напруга:    %.4f V\n", res.v_actual);
        printf("Похибка навантаження: %.2f %%\n", res.error_pct);
    }
    return 0;
}
