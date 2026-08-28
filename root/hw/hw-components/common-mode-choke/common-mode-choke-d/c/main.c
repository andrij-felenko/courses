#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double l_cm_henry;
    double l_leak_henry;
    double fc_cm_hz;
    double fc_dm_hz;
    double i_leak_ma;
    double p_loss_watts;
} cmc_filter_result_t;

cmc_filter_result_t calc_mains_filter(
    double f_noise_hz,
    double att_db,
    double cy_farad,
    double cx_farad,
    double leak_ratio,
    double i_rms_amp,
    double dcr_ohm,
    double v_grid_rms,
    double f_grid_hz)
{
    cmc_filter_result_t res;
    double att_linear = pow(10.0, att_db / 20.0);
    res.fc_cm_hz = f_noise_hz / sqrt(att_linear);
    
    /* Розрахунок L_cm для 2-го порядку: fc = 1 / (2*pi*sqrt(2*L*Cy)) */
    res.l_cm_henry = 1.0 / (8.0 * M_PI * M_PI * res.fc_cm_hz * res.fc_cm_hz * cy_farad);
    res.l_leak_henry = res.l_cm_henry * leak_ratio;
    
    /* Диференційна частота зрізу з Cx */
    res.fc_dm_hz = 1.0 / (2.0 * M_PI * sqrt(res.l_leak_henry * cx_farad));
    
    /* Струм витоку на землю через 2*Cy */
    res.i_leak_ma = (2.0 * M_PI * f_grid_hz * v_grid_rms * (2.0 * cy_farad)) * 1000.0;
    
    /* Теплові втрати на міді двох обмоток */
    res.p_loss_watts = 2.0 * i_rms_amp * i_rms_amp * dcr_ohm;
    
    return res;
}
