#include <cstdint>
#include <array>

class EncoderPipeline {
public:
    struct CalibrationParams {
        int16_t offset_cos{0};
        int16_t offset_sin{0};
        int16_t a11{4096};
        int16_t a12{0};
        int16_t a22{4096};
    };

    explicit EncoderPipeline(const CalibrationParams& params) : params_(params) {}

    int32_t step(uint16_t raw_cos, uint16_t raw_sin) {
        filt_cos_ += (static_cast<int32_t>(raw_cos) - (filt_cos_ >> 4));
        filt_sin_ += (static_cast<int32_t>(raw_sin) - (filt_sin_ >> 4));

        const int16_t u_cos = static_cast<int16_t>(filt_cos_ >> 4) - params_.offset_cos;
        const int16_t u_sin = static_cast<int16_t>(filt_sin_ >> 4) - params_.offset_sin;

        const int16_t v_cos = static_cast<int16_t>((static_cast<int32_t>(params_.a11) * u_cos + 
                                                     static_cast<int32_t>(params_.a12) * u_sin) >> 12);
        const int16_t v_sin = static_cast<int16_t>((static_cast<int32_t>(params_.a22) * u_sin) >> 12);

        const uint16_t curr_angle = calculate_cordic_atan2(v_cos, v_sin);

        const int16_t diff = static_cast<int16_t>(curr_angle - prev_angle_);
        total_position_ += diff;
        prev_angle_ = curr_angle;

        return total_position_;
    }

private:
    static constexpr std::array<uint16_t, 14> CORDIC_LUT16 = {
        8192, 4836, 2555, 1297, 651, 326, 163,
        81, 41, 20, 10, 5, 3, 1
    };

    uint16_t calculate_cordic_atan2(int16_t x, int16_t y) const {
        int32_t x_curr = x;
        int32_t y_curr = y;
        int32_t z_accum = 0;

        if (x_curr < 0) {
            if (y_curr >= 0) {
                const int32_t temp = x_curr;
                x_curr = y_curr;
                y_curr = -temp;
                z_accum = 16384;
            } else {
                const int32_t temp = x_curr;
                x_curr = -y_curr;
                y_curr = temp;
                z_accum = -16384;
            }
        }

        for (std::size_t i = 0; i < CORDIC_LUT16.size(); ++i) {
            int32_t x_next;
            int32_t y_next;
            const uint16_t gamma = CORDIC_LUT16[i];

            if (y_curr > 0) {
                x_next = x_curr + (y_curr >> i);
                y_next = y_curr - (x_curr >> i);
                z_accum += gamma;
            } else {
                x_next = x_curr - (y_curr >> i);
                y_next = y_curr + (x_curr >> i);
                z_accum -= gamma;
            }

            x_curr = x_next;
            y_curr = y_next;
        }

        return static_cast<uint16_t>(z_accum & 0xFFFF);
    }

    CalibrationParams params_;
    int32_t filt_cos_{0};
    int32_t filt_sin_{0};
    uint16_t prev_angle_{0};
    int32_t total_position_{0};
};
