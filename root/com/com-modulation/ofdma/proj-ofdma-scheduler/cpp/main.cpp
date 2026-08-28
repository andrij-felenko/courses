#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <numeric>
#include <iomanip>
#include <algorithm>

struct User {
    int id;
    std::string name;
    float channel_snr_base;      // Середній SNR користувача (дБ)
    float fade_frequency_param;  // Параметр частотного завмирання
    float avg_throughput;        // Накопичена середня швидкість (біт/слот)
    uint64_t total_bits = 0;     // Сумарно передано бітів
    int rbs_allocated_total = 0; // Сумарно виділено RB
};

class OfdmaProportionalFairScheduler {
public:
    static constexpr int NUM_RBS = 25;
    static constexpr float EWMA_WINDOW = 200.0f;

    explicit OfdmaProportionalFairScheduler(std::vector<User> users)
        : users_(std::move(users)) {}

    void simulate(int num_slots) {
        for (int slot = 0; slot < num_slots; ++slot) {
            std::vector<float> slot_bits(users_.size(), 0.0f);
            std::vector<int> slot_rbs(users_.size(), 0);

            // Розподіл кожного ресурсного блоку
            for (int rb = 0; rb < NUM_RBS; ++rb) {
                int best_user = -1;
                float best_metric = -1.0f;
                float best_rate = 0.0f;

                for (size_t u = 0; u < users_.size(); ++u) {
                    float snr = get_instantaneous_snr(users_[u], rb, slot);
                    float achievable_rate = calculate_rb_capacity(snr);
                    float pf_metric = achievable_rate / users_[u].avg_throughput;

                    if (pf_metric > best_metric) {
                        best_metric = pf_metric;
                        best_user = static_cast<int>(u);
                        best_rate = achievable_rate;
                    }
                }

                if (best_user >= 0) {
                    slot_bits[best_user] += best_rate;
                    slot_rbs[best_user]++;
                }
            }

            // Оновлення ковзного середнього (EWMA)
            for (size_t u = 0; u < users_.size(); ++u) {
                users_[u].total_bits += static_cast<uint64_t>(slot_bits[u]);
                users_[u].rbs_allocated_total += slot_rbs[u];

                users_[u].avg_throughput = (1.0f - (1.0f / EWMA_WINDOW)) * users_[u].avg_throughput +
                                           (1.0f / EWMA_WINDOW) * slot_bits[u];
            }
        }
    }

    void print_report(int num_slots) const {
        std::cout << std::left << std::setw(28) << "Користувач" << " | "
                  << std::setw(12) << "Виділено RB" << " | "
                  << std::setw(12) << "Всього Мбіт" << " | "
                  << std::setw(16) << "Швидкість (Мбіт/с)" << "\n";
        std::cout << std::string(75, '-') << "\n";

        uint64_t total_system_bits = 0;
        for (const auto& u : users_) {
            float mbits = static_cast<float>(u.total_bits) / 1'000'000.0f;
            float mbps = static_cast<float>(u.total_bits) / (static_cast<float>(num_slots) * 0.001f * 1'000'000.0f);
            total_system_bits += u.total_bits;

            std::cout << std::left << std::setw(28) << u.name << " | "
                      << std::right << std::setw(9) << u.rbs_allocated_total << " RB | "
                      << std::fixed << std::setprecision(2)
                      << std::setw(9) << mbits << " Мб | "
                      << std::setw(13) << mbps << " Мбіт/с\n";
        }

        float system_mbps = static_cast<float>(total_system_bits) / (static_cast<float>(num_slots) * 0.001f * 1'000'000.0f);
        std::cout << std::string(75, '-') << "\n";
        std::cout << "Сумарна пропускна здатність 20 МГц сектору OFDMA PF: "
                  << std::fixed << std::setprecision(2) << system_mbps << " Мбіт/с\n";
    }

private:
    std::vector<User> users_;

    static float calculate_rb_capacity(float snr_db) {
        float snr_linear = std::pow(10.0f, snr_db / 10.0f);
        float spectral_efficiency = std::log2(1.0f + snr_linear);
        if (spectral_efficiency < 0.5f) return 0.0f;
        if (spectral_efficiency > 8.0f) spectral_efficiency = 8.0f;
        return spectral_efficiency * 140.0f;
    }

    static float get_instantaneous_snr(const User& u, int rb_idx, int slot_idx) {
        float freq_phase = static_cast<float>(rb_idx) * u.fade_frequency_param;
        float time_phase = static_cast<float>(slot_idx) * 0.05f + static_cast<float>(u.id);
        float fast_fading = std::sin(freq_phase + time_phase) * 6.0f + 
                            std::cos(freq_phase * 2.1f + time_phase * 1.7f) * 4.0f;
        return u.channel_snr_base + fast_fading;
    }
};

int main() {
    std::vector<User> initial_users = {
        {0, "UE-A (Центр стільника)", 24.0f, 0.45f, 100.0f},
        {1, "UE-B (Середня зона)",     18.0f, 0.75f, 100.0f},
        {2, "UE-C (Край стільника)",   10.0f, 0.30f, 100.0f},
        {3, "UE-D (IoT термінал)",      6.0f, 0.90f, 100.0f}
    };

    std::cout << "=== Симуляція 2D OFDMA Proportional Fair шедулера (C++) ===\n";
    constexpr int NUM_SLOTS = 1000;

    OfdmaProportionalFairScheduler scheduler(std::move(initial_users));
    scheduler.simulate(NUM_SLOTS);
    scheduler.print_report(NUM_SLOTS);

    return 0;
}
