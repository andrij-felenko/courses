// Обчислення ратіометричного значення та позиції LVDT у C++
#include <cmath>

class LvdtConditioner {
private:
    float sensitivity_km_; // Чутливість k_m (1/мм)

public:
    explicit LvdtConditioner(float sensitivity_km) : sensitivity_km_(sensitivity_km) {}

    float computePosition(float u_s1_rms, float u_s2_rms) const {
        float sum = u_s1_rms + u_s2_rms;
        if (std::abs(sum) < 1e-6f) {
            return 0.0f;
        }
        float r_ratio = (u_s1_rms - u_s2_rms) / sum;
        return r_ratio / sensitivity_km_;
    }
};
