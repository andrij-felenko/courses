#include <iostream>
#include <vector>
#include <string_view>
#include <iomanip>
#include <span>

struct McsProfile {
    std::string_view name;
    float snr_threshold_db;
    float spectral_efficiency;
};

class AmcController {
public:
    static constexpr float kTargetBler = 0.10f;
    static constexpr float kStepUp = 0.10f;
    static constexpr float kStepDown = 0.90f;

    explicit AmcController(float hysteresis_db = 1.2f)
        : hysteresis_db_(hysteresis_db) {}

    void updateOlrc(bool is_ack) noexcept {
        if (is_ack) {
            sinr_offset_db_ += kStepUp;
        } else {
            sinr_offset_db_ -= kStepDown;
        }
    }

    [[nodiscard]] std::size_t selectMcs(float measured_sinr_db, std::span<const McsProfile> mcs_table) noexcept {
        const float eff_sinr = measured_sinr_db + sinr_offset_db_;
        
        // Збільшуємо MCS якщо SINR перевищує поріг + гістерезис
        while (current_mcs_ + 1 < mcs_table.size() &&
               eff_sinr >= mcs_table[current_mcs_ + 1].snr_threshold_db + hysteresis_db_) {
            current_mcs_++;
        }

        // Зменшуємо MCS якщо SINR нижче порогу - гістерезис
        while (current_mcs_ > 0 &&
               eff_sinr < mcs_table[current_mcs_].snr_threshold_db - hysteresis_db_) {
            current_mcs_--;
        }

        return current_mcs_;
    }

    [[nodiscard]] std::size_t currentMcsIndex() const noexcept { return current_mcs_; }
    [[nodiscard]] float offsetDb() const noexcept { return sinr_offset_db_; }

private:
    std::size_t current_mcs_{0};
    float sinr_offset_db_{0.0f};
    float hysteresis_db_{1.2f};
};

int main() {
    constexpr static McsProfile kMcsTable[] = {
        {"QPSK 1/2",    2.5f,  1.0f},
        {"16-QAM 1/2",  7.3f,  2.0f},
        {"16-QAM 3/4", 10.5f,  3.0f},
        {"64-QAM 2/3", 14.3f,  4.0f},
        {"256-QAM 5/6",22.5f,  6.67f}
    };

    AmcController controller(1.2f);
    const std::vector<float> channel_sinr_timeline = {
        3.0f, 4.5f, 9.0f, 12.0f, 16.0f, 24.0f, 20.0f, 8.0f, 2.0f
    };

    std::cout << "=== Симуляція адаптації лінку (C++) ===\n";
    for (std::size_t i = 0; i < channel_sinr_timeline.size(); ++i) {
        const float sinr = channel_sinr_timeline[i];
        const auto mcs_idx = controller.selectMcs(sinr, kMcsTable);
        const auto& profile = kMcsTable[mcs_idx];

        const bool is_ack = (sinr >= profile.snr_threshold_db);
        controller.updateOlrc(is_ack);

        std::cout << "Крок " << std::setw(2) << i << ": SINR = "
                  << std::setw(4) << std::fixed << std::setprecision(1) << sinr << " дБ -> MCS "
                  << mcs_idx << " [" << profile.name << "] (η = "
                  << std::setprecision(2) << profile.spectral_efficiency
                  << ", ACK = " << (is_ack ? "ТАК" : "НІ") << ")\n";
    }

    return 0;
}
