#ifndef LIBFROUDE_H
#define LIBFROUDE_H

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double velocity;        /* Швидкість течії або судна v, м/с */
    double length;          /* Характерний лінійний масштаб L або глибина h, м */
    double gravity;         /* Прискорення вільного падіння g, м/с² */
} froude_input_t;

typedef struct {
    double froude_number;   /* Число Фруда Fr */
    double wave_celerity;   /* Швидкість поверхневих хвиль c = sqrt(g*L), м/с */
    bool is_supercritical;  /* Режим течії: true якщо Fr > 1.0 */
} froude_result_t;

typedef struct {
    double depth_h1;        /* Вхідна глибина до стрибка h1, м */
    double depth_h2;        /* Спряжена глибина після стрибка h2, м */
    double velocity_v1;     /* Швидкість до стрибка v1, м/с */
    double velocity_v2;     /* Швидкість після стрибка v2, м/с */
    double froude_Fr1;      /* Число Фруда до стрибка Fr1 */
    double froude_Fr2;      /* Число Фруда після стрибка Fr2 */
    double energy_loss;     /* Втрата питомої енергії dE, м вод. ст. */
    double power_loss_kw_m; /* Дисипована потужність, кВт/м */
} froude_jump_t;

froude_error_t froude_compute(const froude_input_t* input, froude_result_t* output);
froude_error_t froude_compute_jump(double discharge_q, double depth_h1, froude_jump_t* result);
froude_error_t froude_compute_internal(double velocity, double depth, double rho_upper, 
                                        double rho_lower, double* fr_internal);
const char* froude_strerror(froude_error_t error);

#ifdef __cplusplus
}
#endif

#endif /* LIBFROUDE_H */
