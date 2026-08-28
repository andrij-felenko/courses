#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Фізичні константи в системі SI */
#define C_SPEED 299792458.0             /* швидкість світла у м/с */
#define SEC_PER_YEAR (365.25 * 86400.0)  /* кількість секунд у тропічному році */
#define G_ACCEL 9.80665                 /* стандартне прискорення вільного падіння м/с² */

/* Структура результатів симуляції космічного перельоту */
typedef struct {
    double proper_time_years;   /* власний час мандрівника τ (роки) */
    double earth_time_years;    /* земний час t (роки) */
    double distance_light_years;/* пройдена відстань x (світлові роки) */
    double velocity_c;          /* відносна швидкість (v/c) */
    double gamma;               /* фактор Лоренца γ */
} FlightState;

/* Структура 4-імпульсу релятивістської частинки (у фізичних одиницях ҐеВ) */
typedef struct {
    double energy_gev;          /* повна енергія E (ҐеВ) */
    double px_gev;              /* поздовжній імпульс p_x (ҐеВ/c) */
    double py_gev;              /* поперечний імпульс p_y (ҐеВ/c) */
    double pz_gev;              /* поперечний імпульс p_z (ҐеВ/c) */
} FourMomentum;

/* 
 * Розрахунок гіперболічного руху зі сталим власним прискоренням.
 * proper_years — власний час екіпажу в роках;
 * accel_m_s2 — власне прискорення корабля в м/с² (за замовчуванням 1g).
 */
FlightState simulate_flight(double proper_years, double accel_m_s2) {
    FlightState state;
    state.proper_time_years = proper_years;

    /* Перехід від років до секунд */
    double tau_sec = proper_years * SEC_PER_YEAR;
    
    /* Безрозмірний аргумент гіперболічних функцій α = a·τ / c */
    double alpha = (accel_m_s2 * tau_sec) / C_SPEED;

    /* Обчислення гіперболічних функцій для розрахунку кінематики */
    double sinh_alpha = sinh(alpha);
    double cosh_alpha = cosh(alpha);
    double tanh_alpha = tanh(alpha);

    /* Розрахунок часу Землі t та пройденої відстані x */
    double t_sec = (C_SPEED / accel_m_s2) * sinh_alpha;
    
    /* Стійка чисельна формула через sinh^2 для збереження точності при малих α */
    double sinh_half = sinh(alpha / 2.0);
    double x_meters = (2.0 * C_SPEED * C_SPEED / accel_m_s2) * (sinh_half * sinh_half);

    /* Заповнення вихідної структури */
    state.earth_time_years = t_sec / SEC_PER_YEAR;
    state.distance_light_years = x_meters / (C_SPEED * SEC_PER_YEAR);
    state.velocity_c = tanh_alpha;
    state.gamma = cosh_alpha;

    return state;
}

/* 
 * Перетворення Лоренца для чотири-імпульсу частинки (буст вздовж осі X).
 * in — початковий 4-імпульс у система S;
 * v_c — швидкість руху системи S' відносно S у одиницях c;
 * out — перетворений 4-імпульс у системі S'.
 */
bool boost_four_momentum(const FourMomentum* in, double v_c, FourMomentum* out) {
    if (in == NULL || out == NULL || fabs(v_c) >= 1.0) {
        return false; /* захист від надсвітлових швидкостей та нульових вказівників */
    }

    double gamma = 1.0 / sqrt(1.0 - v_c * v_c);
    
    /* Матричний лоренцівський буст вздовж осі X */
    out->energy_gev = gamma * (in->energy_gev - v_c * in->px_gev);
    out->px_gev     = gamma * (in->px_gev - v_c * in->energy_gev);
    out->py_gev     = in->py_gev;
    out->pz_gev     = in->pz_gev;

    return true;
}

/* Обчислення інваріантної маси спокою частинки m = √((E/c)² - p²) */
double calculate_invariant_mass(const FourMomentum* p) {
    if (p == NULL) return 0.0;
    
    double p2 = p->px_gev * p->px_gev + p->py_gev * p->py_gev + p->pz_gev * p->pz_gev;
    double m2 = p->energy_gev * p->energy_gev - p2;
    
    return (m2 >= 0.0) ? sqrt(m2) : 0.0;
}

int main(void) {
    printf("=========================================================\n");
    printf("  СИМУЛЯЦІЯ РЕЛЯТИВІСТСЬКОГО ПЕРЕЛЬОТУ ТА БУСТУ (C11)\n");
    printf("=========================================================\n\n");

    /* Симуляція експедиції з прискоренням 1g протягом 5 років власного часу */
    double tau_years = 5.0;
    FlightState res = simulate_flight(tau_years, G_ACCEL);

    printf("--- РЕЗУЛЬТАТИ ПЕРЕЛЬОТУ (Прискорення a = 1g) ---\n");
    printf(" Власний час кораблів (tau) : %.2f років\n", res.proper_time_years);
    printf(" Час на Землі (t)           : %.2f років\n", res.earth_time_years);
    printf(" Пройдена відстань (x)       : %.2f св. років\n", res.distance_light_years);
    printf(" Відносна швидкість (v/c)   : %.8f\n", res.velocity_c);
    printf(" Фактор Лоренца (gamma)      : %.2f\n\n", res.gamma);

    /* Демонстрація перетворення 4-імпульсу протона у системі відліку корабля */
    FourMomentum proton_rest = {0.938272, 0.0, 0.0, 0.0}; /* протон у спокої на Землі */
    FourMomentum proton_boosted;

    if (boost_four_momentum(&proton_rest, res.velocity_c, &proton_boosted)) {
        printf("--- БУСТ ЧОТИРИ-ІМПУЛЬСУ ПРОТОНА У СИСТЕМУ КОРАБЛЯ ---\n");
        printf(" Початкова маса у спокої   : %.6f ГеВ/c²\n", calculate_invariant_mass(&proton_rest));
        printf(" Повна енергія у S'        : %.4f ГеВ\n", proton_boosted.energy_gev);
        printf(" Поздовжній імпульс px'    : %.4f ГеВ/c\n", proton_boosted.px_gev);
        printf(" Кінцева інваріанта маса   : %.6f ГеВ/c² (інваріант збережено)\n", 
               calculate_invariant_mass(&proton_boosted));
    }

    return 0;
}
