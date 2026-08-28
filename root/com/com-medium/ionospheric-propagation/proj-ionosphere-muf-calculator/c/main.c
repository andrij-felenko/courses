#include <stdio.h>
#include <math.h>

typedef struct {
    double f_c_mhz;         /* Критична частота (МГц) */
    double muf_mhz;         /* Максимум придатної частоти (МГц) */
    double muf_factor;      /* MUF-фактор sec(theta) */
    double owf_mhz;         /* Оптимальна робоча частота (85% MUF) */
    double skip_dist_km;    /* Відстань стрибка для робочої частоти (км) */
    int is_reflected;       /* 1 якщо промінь повертається на Землю, 0 якщо вилітає */
} iono_path_result_t;

iono_path_result_t calculate_iono_path(double n_e_m3, double layer_h_km, double distance_km, double f_op_mhz) {
    iono_path_result_t res;
    double r_e = 6371.0;
    
    /* Критична частота шару */
    double f_c_hz = 8.98 * sqrt(n_e_m3);
    res.f_c_mhz = f_c_hz / 1.0e6;
    
    /* Кут падіння та корекція сферичності Землі */
    double half_d = distance_km / 2.0;
    double theta_flat = atan2(half_d, layer_h_km);
    double sin_theta_sph = sin(theta_flat) * (r_e / (r_e + layer_h_km));
    if (sin_theta_sph > 1.0) sin_theta_sph = 1.0;
    double cos_theta_sph = sqrt(1.0 - sin_theta_sph * sin_theta_sph);
    
    res.muf_factor = 1.0 / cos_theta_sph;
    res.muf_mhz = res.f_c_mhz * res.muf_factor;
    res.owf_mhz = 0.85 * res.muf_mhz;
    
    if (f_op_mhz <= res.f_c_mhz) {
        /* Сигнал відбивається навіть при вертикальному випромінюванні */
        res.skip_dist_km = 0.0;
        res.is_reflected = 1;
    } else if (f_op_mhz <= res.muf_mhz) {
        /* Обчислення відстані стрибка D_skip */
        double sec_req = f_op_mhz / res.f_c_mhz;
        double cos_req = 1.0 / sec_req;
        double sin_req = sqrt(1.0 - cos_req * cos_req);
        double tan_req = sin_req / cos_req;
        res.skip_dist_km = 2.0 * layer_h_km * tan_req;
        res.is_reflected = 1;
    } else {
        /* Робоча частота вища за MUF — промінь іде у космос */
        res.skip_dist_km = -1.0;
        res.is_reflected = 0;
    }
    
    return res;
}

int main(void) {
    /* Приклад: денний шар F2 (N_e = 1.2e12 ел/м³, h = 300 км, траса D = 2000 км) */
    double n_e = 1.2e12;
    double h = 300.0;
    double distance = 2000.0;
    double f_op = 14.150; /* 20-метровий аматорський діапазон */

    iono_path_result_t res = calculate_iono_path(n_e, h, distance, f_op);

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ІОНОСФЕРНОЇ ТРАСИ ===\n");
    printf("Критична частота f_c : %.2f МГц\n", res.f_c_mhz);
    printf("MUF-фактор           : %.2f\n", res.muf_factor);
    printf("Максимальна частота MUF: %.2f МГц\n", res.muf_mhz);
    printf("Оптимальна частота OWF: %.2f МГц\n", res.owf_mhz);
    printf("Робоча частота f_op  : %.2f МГц\n", f_op);
    
    if (res.is_reflected) {
        printf("Статус: ВІДБИТТЯ УСПІШНЕ\n");
        printf("Відстань стрибка D_skip: %.1f км\n", res.skip_dist_km);
    } else {
        printf("Статус: ПРОБИВАННЯ ІОНОСФЕРИ (сигнал вилітає у космос)\n");
    }

    return 0;
}
