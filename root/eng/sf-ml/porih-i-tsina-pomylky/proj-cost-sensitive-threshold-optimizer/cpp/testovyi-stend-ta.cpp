#include <iostream>
#include <cassert>

void run_cpp_optimizer_tests() {
    using namespace embedded::ml;

    CostMatrix costs{
        .cost_tp = 0.0f,
        .cost_fp = 10.0f,
        .cost_tn = 0.0f,
        .cost_fn = 90.0f
    };

    CalibratorConfig cal{
        .mode = CalibrationMode::Platt,
        .platt_a = 1.0f,
        .platt_b = 0.0f,
        .temperature = 1.0f,
        .table = {},
        .table_size = 0
    };

    AdapterConfig cfg{
        .beta_battery = 2.0f,
        .crit_battery = 0.20f,
        .beta_speed = 1.5f,
        .max_speed_mps = 20.0f,
        .beta_queue = 3.0f,
        .ema_alpha = 1.0f,
        .base_hyst_width = 0.04f,
        .noise_hyst_gain = 0.05f
    };

    auto opt_exp = CostSensitiveThresholdOptimizer::create(costs, cal, cfg, 0.05f);
    assert(opt_exp.has_value());
    auto& opt = *opt_exp;

    assert(std::abs(opt.current_threshold() - 0.10f) < 1e-4f);

    // Номінальний контекст
    AdaptiveContext ctx{
        .battery_ratio = 1.0f,
        .speed_mps = 0.0f,
        .queue_ratio = 0.0f,
        .sensor_noise = 0.01f
    };
    opt.update_context(ctx);

    auto r1 = opt.process_sample(0.0f);
    assert(r1.decision == true);
    assert(std::abs(r1.calibrated_prob - 0.50f) < 1e-3f);

    // Низький заряд батареї
    AdaptiveContext low_batt{
        .battery_ratio = 0.05f,
        .speed_mps = 0.0f,
        .queue_ratio = 0.0f,
        .sensor_noise = 0.01f
    };
    opt.update_context(low_batt);
    assert(opt.current_threshold() > 0.15f);

    std::cout << "Всі тести C++20 пройдено успішно." << std::endl;
}
