#include <cmath>

class InputProcessor {
public:
    static InputError update(uint16_t raw_x, uint16_t raw_y,
                             const InputProfile &profile,
                             InputVector &out_vec) {
        float norm_x = normalizeAxis(raw_x, profile.axis_x);
        float norm_y = normalizeAxis(raw_y, profile.axis_y);

        if (profile.use_radial_deadzone) {
            float mag = std::sqrt(norm_x * norm_x + norm_y * norm_y);
            float dz_in = profile.axis_x.deadzone_inner;
            float dz_out = profile.axis_x.deadzone_outer;

            if (mag <= dz_in) {
                norm_x = 0.0f;
                norm_y = 0.0f;
            } else if (mag >= dz_out) {
                float scale = 1.0f / mag;
                norm_x *= scale;
                norm_y *= scale;
            } else {
                float scale = (mag - dz_in) / (dz_out - dz_in) / mag;
                norm_x *= scale;
                norm_y *= scale;
            }
        }

        out_vec.x = norm_x;
        out_vec.y = norm_y;
        return InputError::Ok;
    }

private:
    static float normalizeAxis(uint16_t raw, const AxisConfig &cfg) {
        if (raw >= cfg.adc_center) {
            uint16_t span = cfg.adc_max - cfg.adc_center;
            return (span > 0) ? static_cast<float>(raw - cfg.adc_center) / span : 0.0f;
        } else {
            uint16_t span = cfg.adc_center - cfg.adc_min;
            return (span > 0) ? -static_cast<float>(cfg.adc_center - raw) / span : 0.0f;
        }
    }
};
