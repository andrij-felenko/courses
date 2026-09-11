#include <cstdint>
#include <algorithm>

class ServoCalibrator {
public:
    ServoCalibrator(uint16_t phys_min_us, 
                    uint16_t phys_max_us, 
                    uint16_t margin_us = 15,
                    float min_deg = 0.0f, 
                    float max_deg = 180.0f)
        : m_t_cal_min(phys_min_us + margin_us),
          m_t_cal_max(phys_max_us - margin_us),
          m_angle_min(min_deg),
          m_angle_max(max_deg),
          m_k_cal(static_cast<float>(m_t_cal_max - m_t_cal_min) / (m_angle_max - m_angle_min)) {}

    // Обчислення безпечної тривалості імпульсу з дворівневим клампінгом
    [[nodiscard]] uint16_t angleToPulse(float target_angle) const noexcept {
        // Рівень 1: кутовий захист від виходу за межі діапазону
        const float clamped_angle = std::clamp(target_angle, m_angle_min, m_angle_max);

        // Лінійна інтерполяція робочого часу
        const float raw_pulse = static_cast<float>(m_t_cal_min) + 
                                m_k_cal * (clamped_angle - m_angle_min);

        // Рівень 2: жорсткий часовий бар'єр для захисту редуктора
        const auto rounded_pulse = static_cast<uint16_t>(raw_pulse + 0.5f);
        return std::clamp(rounded_pulse, m_t_cal_min, m_t_cal_max);
    }

    [[nodiscard]] uint16_t minPulse() const noexcept { return m_t_cal_min; }
    [[nodiscard]] uint16_t maxPulse() const noexcept { return m_t_cal_max; }
    [[nodiscard]] float slope() const noexcept { return m_k_cal; }

private:
    uint16_t m_t_cal_min;
    uint16_t m_t_cal_max;
    float m_angle_min;
    float m_angle_max;
    float m_k_cal;
};
