// dcr_sense_multiphase.hpp - Менеджер багатофазного стабілізатора (C++20)
#pragma once

#include "dcr_sense_channel.hpp"
#include <vector>
#include <span>
#include <numeric>

template <size_t PhaseCount>
class MultiphaseDcrMonitor {
public:
    static_assert(PhaseCount >= 1 && PhaseCount <= 16, "Кількість фаз повинна бути від 1 до 16");

    explicit MultiphaseDcrMonitor(const DcrSenseChannel::Config& cfg) {
        for (auto& ch : channels_) {
            ch = std::make_unique<DcrSenseChannel>(cfg);
        }
    }

    // Калібрування зміщення нуля для всіх каналів
    void calibrate_all_offsets(std::span<const uint16_t, PhaseCount> zero_samples) noexcept {
        for (size_t i = 0; i < PhaseCount; ++i) {
            channels_[i]->calibrate_zero_offset(zero_samples[i]);
        }
    }

    // Оновлення температури фаз від масиву термодатчиків
    void update_phase_temperatures(std::span<const float, PhaseCount> temps_celsius) noexcept {
        for (size_t i = 0; i < PhaseCount; ++i) {
            channels_[i]->update_temperature(temps_celsius[i]);
        }
    }

    // Швидка обробка вибірок струму всіх фаз у перериванні контролера
    [[nodiscard]] float process_all_phases(std::span<const uint16_t, PhaseCount> raw_samples) noexcept {
        float total_current = 0.0f;
        for (size_t i = 0; i < PhaseCount; ++i) {
            total_current += channels_[i]->process_sample(raw_samples[i]);
        }
        return total_current;
    }

    // Отримання доступу до окремого каналу для діагностики та балансування
    [[nodiscard]] const DcrSenseChannel& get_channel(size_t index) const noexcept {
        return *channels_[std::min(index, PhaseCount - 1)];
    }

private:
    std::array<std::unique_ptr<DcrSenseChannel>, PhaseCount> channels_{};
};
