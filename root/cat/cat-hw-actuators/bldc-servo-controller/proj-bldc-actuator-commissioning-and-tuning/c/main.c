#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include "bldc_calib.h"

/*
 * Демонстраційний модуль пусконалагодження та калібрування безколекторного сервопривода.
 * Включає емуляцію силового трифазного моста MOSFET (ШІМ), шунтового вимірювання струмів (АЦП),
 * оптичного/магнітного енкодера та динамічної RL-моделі статора з механікою ротора.
 */

/* Фізичні паспортні параметри двигуна, що моделюється */
#define NOMINAL_R_OHM       0.42f       /* Фазний опір 0.42 Ом */
#define NOMINAL_L_HENRY     0.00018f    /* Фазна індуктивність 180 мкГн */
#define NOMINAL_POLE_PAIRS  7U          /* 7 пар полюсів (14 магнітів на роторі) */
#define ACTUAL_ZERO_OFFSET  1.2566f     /* Реальний механічний зсув нуля енкодера (~72 град) */

/* Структура моделювання апаратної частини сервопривода */
typedef struct {
    /* Напруги, що надходять від вихідного ШІМ-інвертора */
    float va, vb, vc;

    /* Динамічні змінні струму обмоток статора (система координат ротора) */
    float id, iq;

    /* Механічний стан ротора сервомотора */
    float theta_mech_rad;
    float omega_mech_rad_s;

    /* Параметри механічного навантаження привода */
    float rotor_inertia_kg_m2;
    float viscous_damping;
    float torque_constant_nm_a;
} bldc_hardware_sim_t;

/* Глобальний екземпляр апаратної моделі сервопривода */
static bldc_hardware_sim_t g_hw_sim;

/**
 * @brief Ініціалізація апаратної периферії (ШІМ-інвертор, АЦП, таймер енкодера)
 */
static void hardware_peripherals_init(bldc_hardware_sim_t *sim) {
    sim->va = 0.0f;
    sim->vb = 0.0f;
    sim->vc = 0.0f;
    sim->id = 0.0f;
    sim->iq = 0.0f;
    sim->theta_mech_rad = 0.35f; /* Довільне початкове кутове положення вала */
    sim->omega_mech_rad_s = 0.0f;

    sim->rotor_inertia_kg_m2 = 2.5e-5f;
    sim->viscous_damping = 1.2e-4f;
    sim->torque_constant_nm_a = 0.055f;
}

/**
 * @brief Фізична інтеграція електричних та механічних диференціальних рівнянь
 */
static void hardware_physics_step(bldc_hardware_sim_t *sim, float dt) {
    /* Пряме перетворення напруг інвертора у фазну площину alpha-beta */
    float v_alpha = sim->va;
    float v_beta  = (sim->va + 2.0f * sim->vb) * 0.57735026919f;

    /* Справжній фізичний електричний кут ротора */
    float p = (float)NOMINAL_POLE_PAIRS;
    float theta_e_actual = fmodf(p * sim->theta_mech_rad - ACTUAL_ZERO_OFFSET, 6.28318530718f);
    if (theta_e_actual < 0.0f) {
        theta_e_actual += 6.28318530718f;
    }

    /* Проекція напруг на осі d-q ротора */
    float cos_th = cosf(theta_e_actual);
    float sin_th = sinf(theta_e_actual);
    float vd =  v_alpha * cos_th + v_beta * sin_th;
    float vq = -v_alpha * sin_th + v_beta * cos_th;

    /* Диференціальні рівняння RL кола: L*(di/dt) = V - R*i - e_emf */
    float did_dt = (vd - NOMINAL_R_OHM * sim->id) / NOMINAL_L_HENRY;
    float diq_dt = (vq - NOMINAL_R_OHM * sim->iq) / NOMINAL_L_HENRY;

    sim->id += did_dt * dt;
    sim->iq += diq_dt * dt;

    /* Електромагнітний крутний момент та рівняння динаміки ротора */
    float torque_em = sim->torque_constant_nm_a * sim->iq;
    float domega_dt = (torque_em - sim->viscous_damping * sim->omega_mech_rad_s) / sim->rotor_inertia_kg_m2;

    sim->omega_mech_rad_s += domega_dt * dt;
    sim->theta_mech_rad += sim->omega_mech_rad_s * dt;

    /* Нормалізація механічного положення ротора в діапазон [0, 2*PI) */
    sim->theta_mech_rad = fmodf(sim->theta_mech_rad, 6.28318530718f);
    if (sim->theta_mech_rad < 0.0f) {
        sim->theta_mech_rad += 6.28318530718f;
    }
}

/**
 * @brief Апаратний зворотний виклик: оновлення шпаруватості ШІМ інвертора
 */
static void hal_set_phase_voltages(float va, float vb, float vc, void *user_data) {
    bldc_hardware_sim_t *sim = (bldc_hardware_sim_t *)user_data;
    sim->va = va;
    sim->vb = vb;
    sim->vc = vc;
}

/**
 * @brief Апаратний зворотний виклик: опитування шунтових підсилювачів АЦП
 */
static void hal_get_phase_currents(float *ia, float *ib, float *ic, void *user_data) {
    bldc_hardware_sim_t *sim = (bldc_hardware_sim_t *)user_data;

    float p = (float)NOMINAL_POLE_PAIRS;
    float theta_e_actual = fmodf(p * sim->theta_mech_rad - ACTUAL_ZERO_OFFSET, 6.28318530718f);
    if (theta_e_actual < 0.0f) {
        theta_e_actual += 6.28318530718f;
    }

    float cos_th = cosf(theta_e_actual);
    float sin_th = sinf(theta_e_actual);

    /* Зворотний перехід d-q -> alpha-beta для формування фазних струмів */
    float i_alpha = sim->id * cos_th - sim->iq * sin_th;
    float i_beta  = sim->id * sin_th + sim->iq * cos_th;

    *ia = i_alpha;
    *ib = -0.5f * i_alpha + 0.86602540378f * i_beta;
    *ic = -0.5f * i_alpha - 0.86602540378f * i_beta;
}

/**
 * @brief Апаратний зворотний виклик: зчитування положення з таймера енкодера
 */
static float hal_get_encoder_mech_rad(void *user_data) {
    bldc_hardware_sim_t *sim = (bldc_hardware_sim_t *)user_data;
    return sim->theta_mech_rad;
}

int main(void) {
    printf("====================================================================\n");
    printf("  АВТОМАТ КАЛІБРУВАННЯ ТА ІНІЦІАЛІЗАЦІЇ BLDC СЕРВОКОНТРОЛЕРА       \n");
    printf("====================================================================\n\n");

    /* 1. Ініціалізація апаратної периферії */
    hardware_peripherals_init(&g_hw_sim);

    /* 2. Конфігурація параметрів калібрування сервопривода */
    bldc_calib_cfg_t cfg = {
        .v_bus = 24.0f,                   /* 24 В шина живлення інвертора */
        .max_current_a = 5.0f,            /* Поріг відсічки захисту по струму */
        .r_meas_voltage = 0.8f,           /* Напруга вимірювання опору (Id ~ 1.9 А) */
        .l_pulse_voltage = 2.5f,          /* Амплітуда тестових імпульсів індуктивності */
        .open_loop_voltage = 1.5f,        /* Напруга обертання відкритого поля */
        .open_loop_speed_rad_s = 12.566f, /* Швидкість обертання 2 об/с ел. */
        .open_loop_elec_revs = 4.0f,      /* 4 повні електричні оберти */
        .align_voltage = 1.2f,            /* Напруга фіксації електричного нуля */
        .target_bandwidth_hz = 1000.0f,   /* Бажана смуга контуру струму 1 кГц */
        .step_test_current = 1.0f,        /* Амплітуда тестової сходинки 1.0 А */
        .sample_time_s = 0.0001f          /* Крок дискретизації 100 мкс (10 кГц) */
    };

    bldc_calib_hw_ops_t hw_ops = {
        .set_phase_voltages = hal_set_phase_voltages,
        .get_phase_currents = hal_get_phase_currents,
        .get_encoder_mech_rad = hal_get_encoder_mech_rad,
        .user_data = &g_hw_sim
    };

    /* 3. Ініціалізація автомата калібрування */
    bldc_calib_ctx_t calib;
    if (!bldc_calib_init(&calib, &cfg, &hw_ops)) {
        printf("[ПОМИЛКА]: Збій ініціалізації автомата калібрування!\n");
        return -1;
    }

    /* 4. Запуск процедури калібрування */
    if (!bldc_calib_start(&calib)) {
        printf("[ПОМИЛКА]: Не вдалося запустити автомат калібрування!\n");
        return -1;
    }

    bldc_calib_state_t prev_state = BLDC_CALIB_STATE_IDLE;
    uint32_t total_steps = 0U;

    /*
     * 5. Головний цикл виконання: імітація таймерного переривання диспетчера
     * Кожен крок викликає фізичну модель та крок процедурного автомата.
     */
    while (1) {
        hardware_physics_step(&g_hw_sim, cfg.sample_time_s);

        bldc_calib_state_t current_state = bldc_calib_step(&calib);

        /* Сповіщення про перемикання станів скінченного автомата */
        if (current_state != prev_state) {
            float time_ms = (float)total_steps * cfg.sample_time_s * 1000.0f;
            printf("[%7.1f мс] Зміна стану -> %s\n", time_ms, bldc_calib_state_name(current_state));
            prev_state = current_state;
        }

        total_steps++;

        /* Умова виходу: успішне завершення або аварійна зупинка */
        if (current_state == BLDC_CALIB_STATE_COMPLETE || current_state == BLDC_CALIB_STATE_FAULT) {
            break;
        }
    }

    printf("\n====================================================================\n");

    /* 6. Аналіз та звіт результатів ідентифікації */
    if (bldc_calib_get_state(&calib) == BLDC_CALIB_STATE_COMPLETE) {
        printf("  РЕЗУЛЬТАТИ АВТОКАЛІБРУВАННЯ: УСПІШНО ЗАВЕРШЕНО                    \n");
        printf("====================================================================\n\n");

        printf("1. Ідентифіковані параметри двигуна:\n");
        printf("   - Фазний активний опір (R):       %.4f Ом  (еталон: %.4f Ом, похибка: %.1f%%)\n",
               calib.params.resistance_ohm, NOMINAL_R_OHM,
               fabsf(calib.params.resistance_ohm - NOMINAL_R_OHM) / NOMINAL_R_OHM * 100.0f);
        printf("   - Фазна індуктивність (L):        %.2f мкГн (еталон: %.2f мкГн, похибка: %.1f%%)\n",
               calib.params.inductance_henry * 1.0e6f, NOMINAL_L_HENRY * 1.0e6f,
               fabsf(calib.params.inductance_henry - NOMINAL_L_HENRY) / NOMINAL_L_HENRY * 100.0f);
        printf("   - Кількість пар полюсів (p):      %u       (еталон: %u)\n",
               calib.params.pole_pairs, NOMINAL_POLE_PAIRS);
        printf("   - Чергування фаз:                 %s\n",
               calib.params.phase_reversed ? "Інвертоване (B <-> C)" : "Пряме (A -> B -> C)");
        printf("   - Зсув нуля енкодера (theta_0):   %.4f рад (%.2f град)\n\n",
               calib.params.encoder_offset_rad, calib.params.encoder_offset_rad * (180.0f / (float)M_PI));

        printf("2. Розраховані коефіцієнти контуру струму (технічний оптимум):\n");
        printf("   - Смуга пропускання контуру:      %.1f рад/с (%.0f Гц)\n",
               calib.pi_gains.bandwidth_rad_s, calib.pi_gains.bandwidth_rad_s / (2.0f * (float)M_PI));
        printf("   - Пропорційний коефіцієнт (Kp):   %.4f В/А\n", calib.pi_gains.kp);
        printf("   - Інтегральний коефіцієнт (Ki):   %.2f В/(А*с)\n", calib.pi_gains.ki);
        printf("   - Дискретний крок інтегратора (Ki_d): %.5f В/А\n\n", calib.pi_gains.ki_discrete);

        printf("3. Оцінка динаміки за сходинковим відгуком (Id_target = %.1f A):\n",
               calib.step_metrics.target_current_a);
        printf("   - Піковий струм (I_peak):         %.3f А\n", calib.step_metrics.peak_current_a);
        printf("   - Перерегулювання (overshoot):    %.2f %%\n", calib.step_metrics.overshoot_percent);
        printf("   - Час наростання (10%% -> 90%%):     %.2f мс\n", calib.step_metrics.rise_time_ms);
        printf("   - Час встановлення (зона 5%%):     %.2f мс\n", calib.step_metrics.settling_time_ms);
        printf("   - Стійкість перехідного процесу:  %s\n\n",
               calib.step_metrics.stable ? "СТІЙКИЙ (НОРМА)" : "НЕСТІЙКИЙ");

        /* 7. Верифікація готовності до переходу у векторне керування (FOC) */
        float test_mech_angle = 0.5236f; /* 30 механічних градусів */
        float foc_theta_e = bldc_calib_electrical_angle(&calib, test_mech_angle);
        printf("4. Верифікація FOC координатного перетворення:\n");
        printf("   - Для кута вала theta_m = %.4f рад розраховано theta_e = %.4f рад\n",
               test_mech_angle, foc_theta_e);
        printf("   -> Сервопривід готовий до перемикання у штатний режим FOC!\n");
    } else {
        printf("  РЕЗУЛЬТАТИ АВТОКАЛІБРУВАННЯ: АВАРІЙНА ЗУПИНКА                     \n");
        printf("====================================================================\n\n");
        printf("[ПОМИЛКА]: Калібрування перервано. Код: %s (%d)\n",
               bldc_calib_error_name(bldc_calib_get_error(&calib)),
               bldc_calib_get_error(&calib));
    }

    printf("====================================================================\n");
    return 0;
}
