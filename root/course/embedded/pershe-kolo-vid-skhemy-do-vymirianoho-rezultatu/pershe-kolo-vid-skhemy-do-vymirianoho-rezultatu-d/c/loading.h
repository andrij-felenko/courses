#ifndef LOADING_H
#define LOADING_H

/* Корекція ефекту навантаження вимірювальних приладів і оцінка
   паразитних опорів монтажу — те, що інженер рахує на кожному
   вузлі перед тим, як повірити показу приладу. */

typedef enum {
    CALC_OK = 0,
    CALC_BAD_ARG,         /* порожній вказівник або безглузда кількість контактів */
    CALC_BAD_RESISTANCE,  /* опір мусить бути додатним */
    CALC_BAD_CURRENT,     /* струм замалий: ділення на нього дає шум, а не опір */
    CALC_BAD_DROP         /* на виводі чипа напруга вища за джерело — хиба вимірювання */
} calc_err_t;

const char *calc_err_text(calc_err_t err);

/* Статус рядка інженерного протоколу. */
typedef enum {
    V_PASS = 0,  /* у межах допуску */
    V_WARN,      /* пояснюється похибкою навантаження, потребує корекції */
    V_FAIL       /* дефект */
} verdict_t;

const char *verdict_text(verdict_t v);

/* Еквівалент Тевеніна вузла: генератор напруги плюс вихідний опір. */
typedef struct {
    double u_th;  /* напруга холостого ходу, В */
    double r_th;  /* вихідний опір вузла, Ом */
} thevenin_t;

calc_err_t thevenin_of_divider(double u_supply, double r_top, double r_bottom,
                               thevenin_t *out);

/* Показ вольтметра поруч з істинним значенням вузла. */
typedef struct {
    double u_true;     /* напруга холостого ходу, В */
    double u_meas;     /* що покаже (або показав) прилад, В */
    double error_pct;  /* (u_meas - u_true) / u_true, % — завжди <= 0 */
    double ratio;      /* R_m / R_th: те, що судить «золоте правило» */
    verdict_t verdict; /* R_m >= 100 * R_th ? */
} loading_t;

/* Пряма задача: вузол відомий — яким його побачить прилад із опором r_meter. */
calc_err_t voltmeter_reading(const thevenin_t *node, double r_meter, loading_t *out);

/* Обернена задача: відомий лише показ — відновлюємо істинну U_th вузла. */
calc_err_t correct_loading(double u_meas, double r_th, double r_meter, loading_t *out);

/* Струм гілки за падінням на прецизійному шунті: I = U_shunt / R_shunt. */
calc_err_t shunt_current(double u_shunt, double r_shunt, double *i_out);

/* Оцінка паразитного опору шляху живлення й одного контакту макетки. */
typedef struct {
    double i_branch;       /* струм гілки, А */
    double u_drop;         /* просідання шини від джерела до виводу чипа, В */
    double r_path;         /* сумарний опір шляху, Ом */
    double r_per_contact;  /* на один контакт, Ом */
    verdict_t verdict;     /* за нормами клем макетки: 0.3 / 0.5 Ом */
} contact_t;

calc_err_t estimate_contact_resistance(double u_supply, double u_shunt, double u_pin,
                                       double r_shunt, int contacts, contact_t *out);

#endif /* LOADING_H */
