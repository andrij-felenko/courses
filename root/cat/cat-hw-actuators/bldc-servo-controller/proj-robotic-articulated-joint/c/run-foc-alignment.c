// Алгоритм фіксації нуля та обчислення offset електричного кута
#include <stdint.h>
#include <math.h>

typedef struct {
    float theta_offset;
    int8_t direction;
    uint8_t pole_pairs;
    uint8_t calibrated;
} foc_calib_t;

void run_foc_alignment(foc_calib_t *calib, float (*read_encoder_rad)(void), void (*set_id_iq)(float id, float iq, float theta_el)) {
    // 1. Подача струму вирівнювання вздовж d-осі
    float i_align = 2.0f; // Струм вирівнювання в Амперах
    set_id_iq(i_align, 0.0f, 0.0f);
    
    // Затримка для заспокоєння механічних коливань
    for (volatile int i = 0; i < 1000000; i++);

    // 2. Підхід із позитивного боку
    set_id_iq(i_align, 0.0f, 0.2f);
    for (volatile int i = 0; i < 500000; i++);
    set_id_iq(i_align, 0.0f, 0.0f);
    for (volatile int i = 0; i < 500000; i++);
    float pos_angle = read_encoder_rad();

    // 3. Підхід із негативного боку
    set_id_iq(i_align, 0.0f, -0.2f);
    for (volatile int i = 0; i < 500000; i++);
    set_id_iq(i_align, 0.0f, 0.0f);
    for (volatile int i = 0; i < 500000; i++);
    float neg_angle = read_encoder_rad();

    // 4. Обчислення середнього механічного нуля та електричного зсуву
    float mech_zero = (pos_angle + neg_angle) * 0.5f;
    calib->theta_offset = fmodf(calib->pole_pairs * mech_zero, 2.0f * M_PI);
    if (calib->theta_offset < 0.0f) {
        calib->theta_offset += 2.0f * M_PI;
    }
    calib->calibrated = 1;
    
    // Зняття струму вирівнювання
    set_id_iq(0.0f, 0.0f, 0.0f);
}
