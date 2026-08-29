/*
 * Показовий прогін модуля просторових перетворень.
 * Збірка: cc -std=c11 -O2 c/*.c -lm -o axes-demo
 */
#include "ahrs.h"
#include "calib6.h"
#include "sensor_align.h"

#include <stdio.h>

#define PI_F     3.14159265358979f
#define RAD2DEG  (180.0f / PI_F)
#define DEG2RAD  (PI_F / 180.0f)

static void print_vec(const char *tag, vec3_t v) {
    printf("  %-26s [% .5f % .5f % .5f]\n", tag, (double)v.x, (double)v.y, (double)v.z);
}

static void print_mat(const char *tag, mat3_t m) {
    printf("  %s\n", tag);
    for (int i = 0; i < 3; ++i)
        printf("      [% .4f % .4f % .4f]\n",
               (double)m.m[i][0], (double)m.m[i][1], (double)m.m[i][2]);
}

/* Свій генератор шуму: прогін має повторюватися байт у байт на будь-якій машині. */
static unsigned rng_state = 20260829u;
static float noise(float amplitude) {
    rng_state = rng_state * 1664525u + 1013904223u;
    float u = (float)((rng_state >> 8) & 0xFFFFu) / 65535.0f;   /* [0, 1] */
    return (u - 0.5f) * 2.0f * amplitude;
}

static void demo_frames(void) {
    puts("== 1. Світові базиси: NED <-> ENU ==");
    vec3_t v_ned = vec3_make(12.0f, -3.0f, -50.0f);   /* північ, схід, вниз: висота 50 м */
    vec3_t v_enu = frame_swap_ned_enu(v_ned);
    print_vec("v_ned (N, E, D)", v_ned);
    print_vec("v_enu (E, N, U)", v_enu);
    print_vec("назад у NED", frame_swap_ned_enu(v_enu));

    mat3_t p_ned = { { { 0.25f, 0.02f, 0.00f },
                       { 0.02f, 0.30f, 0.00f },
                       { 0.00f, 0.00f, 1.20f } } };
    print_mat("P_enu = T·P_ned·Tᵀ", frame_swap_cov_ned_enu(p_ned));
    printf("  слід коваріації зберігся: %.4f -> %.4f\n",
           (double)(p_ned.m[0][0] + p_ned.m[1][1] + p_ned.m[2][2]),
           (double)(frame_swap_cov_ned_enu(p_ned).m[0][0] +
                    frame_swap_cov_ned_enu(p_ned).m[1][1] +
                    frame_swap_cov_ned_enu(p_ned).m[2][2]));
}

static void demo_mounting(void) {
    puts("\n== 2. Плата, перекіс і конвеєр вирівнювання ==");
    mat3_t table[64];
    printf("  унікальних дискретних орієнтацій плати: %d\n",
           board_rotation_enumerate(table, 64));

    sensor_calib_t cal;
    sensor_calib_identity(&cal);

    /* Плата стоїть носом праворуч: у тіло вектор переходить поворотом на −90° за курсом. */
    board_rotation_t rot = { 0, 0, 3 };
    sensor_calib_set_board(&cal, rot);
    print_mat("R_board (YAW_90)", cal.r_board);

    mat3_t s = { { {  1.0120f,  0.0040f, -0.0020f },
                   {  0.0040f,  0.9910f,  0.0030f },
                   { -0.0020f,  0.0030f,  1.0070f } } };
    sensor_calib_set_scale(&cal, s);

    if (!sensor_calib_set_misalignment(&cal, vec3_make(0.4f * DEG2RAD,
                                                       2.0f * DEG2RAD,
                                                      -0.7f * DEG2RAD))) {
        puts("  перекіс поза межами малокутової моделі — калібрування відхилено");
        return;
    }

    vec3_t poly[4] = {
        { 0.0500f, -0.0300f,  0.1100f },   /* b0, м/с² */
        { 0.0008f, -0.0005f,  0.0012f },   /* b1, м/с²/°C */
        { 0.0000f,  0.0000f,  0.0000f },
        { 0.0000f,  0.0000f,  0.0000f }
    };
    sensor_calib_set_bias_poly(&cal, poly, 25.0f);

    float ortho = 0.0f;
    if (!sensor_calib_check(&cal, &ortho)) {
        printf("  калібрування зіпсоване, похибка ортогональності %.2e\n", (double)ortho);
        return;
    }
    printf("  похибка ортогональності поворотів: %.2e\n", (double)ortho);

    print_vec("b_bias(+25 °C)", sensor_bias_at(&cal, 25.0f));
    print_vec("b_bias(+60 °C)", sensor_bias_at(&cal, 60.0f));

    /* Числа з розділу про такт польотного контролера, переведені в м/с². */
    vec3_t a_raw = vec3_scale(vec3_make(0.02f, -0.05f, 1.01f), AHRS_GRAVITY);
    print_vec("a_raw (сенсор)", a_raw);
    print_vec("a_body (FRD, +60 °C)", sensor_align_measurement(&cal, a_raw, 60.0f));

    /* Ціна нескомпенсованого перекосу: розгін уперед протікає на поперечну вісь. */
    float lie = 10.0f * sinf(2.0f * DEG2RAD);
    printf("  перекіс 2.0° при розгоні 10 м/с² дає хибні %.3f м/с² на осі Y\n", (double)lie);
}

/* Розв'язок M·x = t для нижньої трикутної M — потрібен, щоб зліпити синтетичні виміри. */
static vec3_t lower_solve(mat3_t m, vec3_t t) {
    float x0 = t.x / m.m[0][0];
    float x1 = (t.y - m.m[1][0] * x0) / m.m[1][1];
    float x2 = (t.z - m.m[2][0] * x0 - m.m[2][1] * x1) / m.m[2][2];
    return vec3_make(x0, x1, x2);
}

static void demo_calibration(void) {
    puts("\n== 3. Статичне калібрування акселерометра ==");

    /* Правда, якої алгоритм не знає. */
    mat3_t m_true = { { {  1.0200f,  0.0f,     0.0f    },
                        {  0.0100f,  0.9800f,  0.0f    },
                        { -0.0080f,  0.0120f,  1.0100f } } };
    vec3_t b_true = vec3_make(0.1500f, -0.2200f, 0.3100f);

    const float k = 0.57735027f;   /* 1/sqrt(3) — кутові положення куба */
    const vec3_t dir[14] = {
        {  1, 0, 0 }, { -1, 0, 0 }, { 0,  1, 0 }, { 0, -1, 0 }, { 0, 0,  1 }, { 0, 0, -1 },
        {  k,  k,  k }, {  k,  k, -k }, {  k, -k,  k }, {  k, -k, -k },
        { -k,  k,  k }, { -k,  k, -k }, { -k, -k,  k }, { -k, -k, -k }
    };

    vec3_t avg[14];
    for (int i = 0; i < 14; ++i) {
        /* Ідеальний вимір: M·(a − b) = g·dir, тобто a = M⁻¹·(g·dir) + b. */
        vec3_t ideal = vec3_add(lower_solve(m_true, vec3_scale(dir[i], AHRS_GRAVITY)), b_true);
        vec3_t burst[64];
        for (int s = 0; s < 64; ++s) {
            burst[s] = vec3_add(ideal, vec3_make(noise(0.02f), noise(0.02f), noise(0.02f)));
        }
        if (!calib6_still_average(burst, 64, 0.30f, &avg[i])) {
            printf("  позиція %d: апарат не стояв, набір відкинуто\n", i);
            return;
        }
    }

    calib6_result_t diag;
    calib6_status_t st = calib6_solve(avg, 6, AHRS_GRAVITY, CALIB6_MODEL_DIAGONAL, &diag);
    printf("  6 граней, діагональна модель: %s\n", calib6_status_text(st));
    if (st == CALIB6_OK) {
        printf("    масштаби [% .4f % .4f % .4f], ітерацій %d, RMS %.4f%% g\n",
               (double)diag.m.m[0][0], (double)diag.m.m[1][1], (double)diag.m.m[2][2],
               diag.iterations, (double)diag.rms_rel * 100.0);
        print_vec("bias знайдений", diag.bias);
    }

    /* Шість граней дають шість рівнянь — на дев'ять невідомих їх бракує. */
    calib6_result_t bad;
    printf("  6 граней, тривісна модель: %s\n",
           calib6_status_text(calib6_solve(avg, 6, AHRS_GRAVITY, CALIB6_MODEL_TRIAXIAL, &bad)));

    calib6_result_t full;
    st = calib6_solve(avg, 14, AHRS_GRAVITY, CALIB6_MODEL_TRIAXIAL, &full);
    printf("  14 положень, тривісна модель: %s\n", calib6_status_text(st));
    if (st == CALIB6_OK) {
        print_mat("M знайдена", full.m);
        print_mat("M справжня", m_true);
        print_vec("bias знайдений", full.bias);
        print_vec("bias справжній", b_true);
        printf("    ітерацій %d, RMS %.4f%% g\n", full.iterations, (double)full.rms_rel * 100.0);
    }
}

static void demo_coning(void) {
    puts("\n== 4. Конічний рух: що губить просте підсумовування приростів ==");
    const float amp = 0.02f;                 /* кутова амплітуда коливання, рад */
    const float freq = 100.0f;               /* частота вібрації, Гц */
    const float w = 2.0f * PI_F * freq;
    const float dt_fast = 0.0005f;           /* швидкий контур 2 кГц */
    const int   slow_div = 8;                /* повільний контур 250 Гц */
    const int   steps = 4000;                /* 2 секунди */

    ahrs_t with_c, without_c;
    ahrs_init(&with_c, 0.0f, 0.0f, true);
    ahrs_init(&without_c, 0.0f, 0.0f, false);

    for (int k = 0; k < steps; ++k) {
        float t = (float)k * dt_fast;
        /* p і q зсунуті по фазі на 90°: амплітуда швидкості A·ω. */
        vec3_t omega = vec3_make(amp * w * sinf(w * t), amp * w * cosf(w * t), 0.0f);
        ahrs_push_gyro(&with_c, omega, dt_fast);
        ahrs_push_gyro(&without_c, omega, dt_fast);
        if ((k + 1) % slow_div == 0) {
            ahrs_update(&with_c, NULL, dt_fast * (float)slow_div);
            ahrs_update(&without_c, NULL, dt_fast * (float)slow_div);
        }
    }

    float seconds = (float)steps * dt_fast;
    float yaw_with = ahrs_euler(&with_c).yaw * RAD2DEG;
    float yaw_without = ahrs_euler(&without_c).yaw * RAD2DEG;
    printf("  теоретичний дрейф 0.5·A²·ω = %.3f °/с\n", (double)(0.5f * amp * amp * w * RAD2DEG));
    printf("  з конічною поправкою: курс %+8.3f°  (%.3f °/с)\n",
           (double)yaw_with, (double)(yaw_with / seconds));
    printf("  без поправки:         курс %+8.3f°  (%.3f °/с)\n",
           (double)yaw_without, (double)(yaw_without / seconds));
    printf("  розбіжність за 2 с:   %+8.3f°\n", (double)(yaw_with - yaw_without));
}

static void demo_complementary(void) {
    puts("\n== 5. Корекція за вертикаллю і вивчення зсуву гіроскопа ==");
    ahrs_t f;
    ahrs_init(&f, 1.2f, 0.10f, true);

    const float true_roll = 20.0f * DEG2RAD;
    vec3_t accel = vec3_make(0.0f,
                             sinf(true_roll) * AHRS_GRAVITY,
                             cosf(true_roll) * AHRS_GRAVITY);
    vec3_t gyro_reading = vec3_make(0.02f, -0.01f, 0.0f);   /* самий лише зсув нуля, рад/с */

    const float dt_fast = 0.001f;
    for (int step = 0; step < 5000; ++step) {               /* 5 секунд */
        ahrs_push_gyro(&f, gyro_reading, dt_fast);
        if ((step + 1) % 4 == 0) ahrs_update(&f, &accel, 4.0f * dt_fast);
        if ((step + 1) % 1000 == 0) {
            euler_t e = ahrs_euler(&f);
            printf("  t=%.0f c  крен %6.2f°  тангаж %6.2f°  зсув гіро [% .4f % .4f] рад/с\n",
                   (double)((float)(step + 1) * dt_fast),
                   (double)(e.roll * RAD2DEG), (double)(e.pitch * RAD2DEG),
                   (double)f.gyro_bias.x, (double)f.gyro_bias.y);
        }
    }
    printf("  істина: крен %.2f°, зсув [% .4f % .4f]; акселерометр відхилено %u разів\n",
           (double)(true_roll * RAD2DEG), (double)gyro_reading.x, (double)gyro_reading.y,
           f.accel_rejected);
}

static void demo_gimbal_lock(void) {
    puts("\n== 6. Шарнірний замок у кінематиці Ейлера ==");
    vec3_t omega = vec3_make(0.0f, 0.0f, 0.01f);   /* шум гіроскопа 0.01 рад/с */
    const float pitches[3] = { 0.0f, 89.9f, 89.99999f };
    for (int i = 0; i < 3; ++i) {
        euler_t angles = { 0.0f, pitches[i] * DEG2RAD, 0.0f };
        euler_t rates;
        if (euler_rates_from_gyro(angles, omega, &rates)) {
            printf("  тангаж %9.5f°: dψ/dt = %10.3f °/с\n",
                   (double)pitches[i], (double)(rates.yaw * RAD2DEG));
        } else {
            printf("  тангаж %9.5f°: сингулярність, кути Ейлера тут не визначені\n",
                   (double)pitches[i]);
        }
    }
    /* Кватерніон тієї самої орієнтації жодної особливої точки не має. */
    euler_t straight_up = { 0.0f, 90.0f * DEG2RAD, 0.0f };
    quat_t q = quat_from_euler(straight_up);
    vec3_t nose_world = quat_rotate(q, vec3_make(1.0f, 0.0f, 0.0f));
    print_vec("ніс у світі при θ=90°", nose_world);
    printf("  норма кватерніона: %.7f\n", (double)quat_norm(q));
}

static void demo_interpolation(void) {
    puts("\n== 7. Інтегрування великого кроку та інтерполяція ==");
    vec3_t omega = vec3_make(0.0f, 0.0f, 400.0f * DEG2RAD);   /* швидке рискання */
    float dt = 0.001f;
    quat_t linear = quat_integrate_gyro(quat_identity(), omega, dt);
    quat_t exact = quat_mul(quat_identity(), quat_from_rotation_vector(vec3_scale(omega, dt)));
    printf("  за 1 мс при 400 °/с: Ейлер 1-го порядку %.6f°, експонента %.6f°\n",
           (double)(quat_to_euler(linear).yaw * RAD2DEG),
           (double)(quat_to_euler(exact).yaw * RAD2DEG));

    euler_t e1 = { 0.0f, 0.0f, 0.0f };
    euler_t e2 = { 0.0f, 0.0f, 90.0f * DEG2RAD };
    quat_t q1 = quat_from_euler(e1), q2 = quat_from_euler(e2);
    printf("  дуга 90°, t=0.5:  slerp %.4f°  nlerp %.4f°\n",
           (double)(quat_to_euler(quat_slerp(q1, q2, 0.5f)).yaw * RAD2DEG),
           (double)(quat_to_euler(quat_nlerp(q1, q2, 0.5f)).yaw * RAD2DEG));

    euler_t e3 = { 0.0f, 0.0f, 5.0f * DEG2RAD };
    quat_t q3 = quat_from_euler(e3);
    printf("  дуга 5°,  t=0.5:  slerp %.6f°  nlerp %.6f°\n",
           (double)(quat_to_euler(quat_slerp(q1, q3, 0.5f)).yaw * RAD2DEG),
           (double)(quat_to_euler(quat_nlerp(q1, q3, 0.5f)).yaw * RAD2DEG));
}

int main(void) {
    demo_frames();
    demo_mounting();
    demo_calibration();
    demo_coning();
    demo_complementary();
    demo_gimbal_lock();
    demo_interpolation();
    return 0;
}
