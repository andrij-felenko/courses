#include <stdio.h>
#include <math.h>

#define CISPR32_CLASS_B_3M_DBUV 40.0

typedef struct {
    double mutual_capacitance_pf; // Паразитна ємність (пФ)
    double aggressor_dv;          // Перепад напруги (В)
    double rise_time_ns;          // Час наростання фронту (нс)
    double victim_impedance_ohm;   // Вхідний опір жертви (Ом)
} CapacitiveCouplingParams;

typedef struct {
    double mutual_inductance_nh;  // Взаємна індуктивність (нГн)
    double aggressor_di;          // Перепад струму (А)
    double rise_time_ns;          // Час наростання фронту (нс)
} InductiveCouplingParams;

typedef struct {
    double common_resistance_mohm; // Активний опір спільної ділянки (мОм)
    double common_inductance_nh;   // Паразитна індуктивність ділянки (нГн)
    double pulse_current_a;        // Амплітуда імпульсу струму (А)
    double rise_time_ns;          // Час наростання (нс)
} GroundBounceParams;

typedef struct {
    double frequency_mhz;         // Частота гармоніки (МГц)
    double loop_area_cm2;         // Площа сигнального контуру (см²)
    double diff_current_ma;       // Диференційний струм (мА)
    double cable_length_m;        // Довжина кабелю (м)
    double common_mode_current_ua; // Синфазний струм (мкА)
    double distance_m;            // Відстань до антени (м)
} RadiationParams;

double calculate_capacitive_noise(const CapacitiveCouplingParams *p, double *injected_current_ma) {
    double c_farads = p->mutual_capacitance_pf * 1e-12;
    double dt_sec = p->rise_time_ns * 1e-9;
    double dv_dt = p->aggressor_dv / dt_sec;
    double current_a = c_farads * dv_dt;

    if (injected_current_ma) {
        *injected_current_ma = current_a * 1e3;
    }
    return current_a * p->victim_impedance_ohm;
}

double calculate_inductive_noise(const InductiveCouplingParams *p) {
    double m_henry = p->mutual_inductance_nh * 1e-9;
    double dt_sec = p->rise_time_ns * 1e-9;
    double di_dt = p->aggressor_di / dt_sec;
    return m_henry * di_dt;
}

double calculate_ground_bounce(const GroundBounceParams *p) {
    double r_ohm = p->common_resistance_mohm * 1e-3;
    double l_henry = p->common_inductance_nh * 1e-9;
    double dt_sec = p->rise_time_ns * 1e-9;
    double di_dt = p->pulse_current_a / dt_sec;

    double v_resistive = p->pulse_current_a * r_ohm;
    double v_inductive = l_henry * di_dt;
    return v_resistive + v_inductive;
}

void calculate_radiated_field(const RadiationParams *p, double *e_dm_dbuv, double *e_cm_dbuv) {
    double f_hz = p->frequency_mhz * 1e6;
    double a_m2 = p->loop_area_cm2 * 1e-4;
    double i_dm_a = p->diff_current_ma * 1e-3;
    double i_cm_a = p->common_mode_current_ua * 1e-6;

    // Диференційне випромінювання контуру з відбиттям: E_DM = (2.632e-14 * f^2 * I * A) / r
    double e_dm_vm = (2.632e-14 * f_hz * f_hz * i_dm_a * a_m2) / p->distance_m;
    double e_dm_uvm = e_dm_vm * 1e6;
    *e_dm_dbuv = 20.0 * log10(e_dm_uvm > 1e-9 ? e_dm_uvm : 1e-9);

    // Синфазне випромінювання кабелю з відбиттям: E_CM = (1.257e-6 * f * I * L) / r
    double e_cm_vm = (1.257e-6 * f_hz * i_cm_a * p->cable_length_m) / p->distance_m;
    double e_cm_uvm = e_cm_vm * 1e6;
    *e_cm_dbuv = 20.0 * log10(e_cm_uvm > 1e-9 ? e_cm_uvm : 1e-9);
}

int main(void) {
    printf("=== Інженерний розрахунок параметрів ЕМС ===\n\n");

    CapacitiveCouplingParams cap = { .mutual_capacitance_pf = 3.0, .aggressor_dv = 3.3, .rise_time_ns = 1.0, .victim_impedance_ohm = 10000.0 };
    double inj_ma = 0.0;
    double v_cap = calculate_capacitive_noise(&cap, &inj_ma);
    printf("1. Ємнісний зв'язок:\n");
    printf("   Паразитна ємність: %.1f пФ, фронт: %.1f нс, навантаження: %.1f кОм\n", cap.mutual_capacitance_pf, cap.rise_time_ns, cap.victim_impedance_ohm / 1000.0);
    printf("   Впорснутий струм: %.3f мА -> Наведена напруга на жертві: %.3f В\n\n", inj_ma, v_cap);

    InductiveCouplingParams ind = { .mutual_inductance_nh = 4.5, .aggressor_di = 2.0, .rise_time_ns = 5.0 };
    double v_ind = calculate_inductive_noise(&ind);
    printf("2. Індуктивний зв'язок:\n");
    printf("   Взаємна індуктивність: %.1f нГн, струм: %.1f А за %.1f нс\n", ind.mutual_inductance_nh, ind.aggressor_di, ind.rise_time_ns);
    printf("   Наведена напруга: %.3f В (%.1f мВ)\n\n", v_ind, v_ind * 1e3);

    GroundBounceParams gb = { .common_resistance_mohm = 5.0, .common_inductance_nh = 2.5, .pulse_current_a = 4.0, .rise_time_ns = 2.0 };
    double v_gb = calculate_ground_bounce(&gb);
    printf("3. Зсув опорного нуля (Ground Bounce):\n");
    printf("   Спільна земля: %.1f мОм, %.1f нГн, імпульс: %.1f А за %.1f нс\n", gb.common_resistance_mohm, gb.common_inductance_nh, gb.pulse_current_a, gb.rise_time_ns);
    printf("   Стрибок потенціалу землі: %.3f В (%.1f мВ)\n\n", v_gb, v_gb * 1e3);

    RadiationParams rad = { .frequency_mhz = 100.0, .loop_area_cm2 = 1.5, .diff_current_ma = 25.0, .cable_length_m = 1.2, .common_mode_current_ua = 8.0, .distance_m = 3.0 };
    double e_dm_db = 0.0, e_cm_db = 0.0;
    calculate_radiated_field(&rad, &e_dm_db, &e_cm_db);
    printf("4. Випромінюване поле на частоті %.1f МГц (дистанція %.1f м):\n", rad.frequency_mhz, rad.distance_m);
    printf("   Контур (DM): струм %.1f мА, площа %.2f см² -> Поле: %.1f дБмкВ/м (Ліміт CISPR-B: %.1f)\n", rad.diff_current_ma, rad.loop_area_cm2, e_dm_db, CISPR32_CLASS_B_3M_DBUV);
    printf("   Кабель (CM): струм %.1f мкА, довжина %.1f м -> Поле: %.1f дБмкВ/м (Ліміт CISPR-B: %.1f)\n", rad.common_mode_current_ua, rad.cable_length_m, e_cm_db, CISPR32_CLASS_B_3M_DBUV);

    return 0;
}
