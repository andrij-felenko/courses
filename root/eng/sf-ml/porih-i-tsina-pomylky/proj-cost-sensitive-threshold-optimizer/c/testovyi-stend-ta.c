#include <stdio.h>
#include <assert.h>

void run_embedded_optimizer_tests(void) {
    c_cost_matrix_t base_costs = {
        .cost_tp = 0.0f,
        .cost_fp = 10.0f,
        .cost_tn = 0.0f,
        .cost_fn = 90.0f
    };
    
    c_calibrator_config_t cal = {
        .mode = CALIB_MODE_PLATT,
        .platt_a = 1.0f,
        .platt_b = 0.0f,
        .temperature = 1.0f,
        .table_size = 0
    };
    
    c_adapter_config_t cfg = {
        .beta_battery = 2.0f,
        .crit_battery = 0.20f,
        .beta_speed = 1.5f,
        .max_speed_mps = 20.0f,
        .beta_queue = 3.0f,
        .ema_alpha = 1.0f, /* Миттєве застосування для детермінізму тесту */
        .base_hyst_width = 0.04f,
        .noise_hyst_gain = 0.05f
    };
    
    c_threshold_optimizer_t opt;
    bool init_ok = c_optimizer_init(&opt, base_costs, cal, cfg, 0.05f);
    assert(init_ok);
    assert(fabsf(opt.current_threshold - 0.10f) < 1e-4f);
    
    /* Тест 1: Перевірка базової класифікації */
    c_adaptive_context_t nominal_ctx = {
        .battery_ratio = 1.0f,
        .speed_mps = 0.0f,
        .queue_ratio = 0.0f,
        .sensor_noise = 0.01f
    };
    c_optimizer_update_context(&opt, nominal_ctx);
    
    /* Подаємо логіт z = 0.0 => p = 0.50 > T*(0.10) => Decision True */
    c_decision_result_t r1 = c_optimizer_process_sample(&opt, 0.0f);
    assert(r1.decision == true);
    assert(fabsf(r1.calibrated_prob - 0.50f) < 1e-3f);
    
    /* Тест 2: Перевірка гістерезису */
    /* За T* = 0.10 та попереднього стану True поріг вимкнення: 0.10 - 0.02 = 0.08 */
    /* Подаємо логіт, що дає p = 0.09 (вище 0.08, але нижче 0.10) => має лишитися True */
    float z_hyst = logf(0.09f / (1.0f - 0.09f)); /* logit для p = 0.09 */
    c_decision_result_t r2 = c_optimizer_process_sample(&opt, z_hyst);
    assert(r2.decision == true);
    
    /* Тест 3: Вичерпання батареї підіймає поріг */
    c_adaptive_context_t low_batt_ctx = {
        .battery_ratio = 0.05f, /* 5% заряду */
        .speed_mps = 0.0f,
        .queue_ratio = 0.0f,
        .sensor_noise = 0.01f
    };
    c_optimizer_update_context(&opt, low_batt_ctx);
    assert(opt.current_threshold > 0.15f);
    
    printf("Всі вбудовані тести C99 пройдено успішно.\n");
}
