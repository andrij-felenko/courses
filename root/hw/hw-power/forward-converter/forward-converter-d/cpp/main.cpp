#include <algorithm>
#include <cstdint>

// Обчислення безпечної шпаруватості ШІМ для Forward-перетворювача
class ForwardController {
public:
    struct Config {
        float np_ns_ratio{1.272f};
        float np_nr_ratio{1.000f};
        float hard_duty_limit{0.450f};
    };

    explicit ForwardController(Config cfg) : cfg_(cfg) {}

    [[nodiscard]] float compute_safe_duty(float vin, float vout) const noexcept {
        if (vin <= 1.0f) return 0.0f;

        // Теоретична межа вольт-секундного балансу: D < 1 / (1 + Nr/Np)
        const float d_max_theoretical = 1.0f / (1.0f + cfg_.np_nr_ratio);
        const float d_safe_ceiling = std::min(d_max_theoretical - 0.05f, cfg_.hard_duty_limit);

        const float d_target = (vout / vin) * cfg_.np_ns_ratio;
        return std::clamp(d_target, 0.05f, d_safe_ceiling);
    }

private:
    Config cfg_;
};
