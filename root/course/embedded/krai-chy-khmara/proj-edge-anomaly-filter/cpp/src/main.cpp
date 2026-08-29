/*
 * Прогін модуля на хості: синтетичний сигнал замість АЦП, друк рішень
 * замість радіо. Збірка:
 *   c++ -std=c++20 -Iinclude src/main.cpp src/telemetry_frame.cpp -o edge_demo
 * (rtos_tasks.cpp потребує FreeRTOS і в хостову збірку не входить).
 *
 * Сценарій навмисно містить усе, на чому модуль ламався б: розігрів, стабільну
 * норму, повільний дрейф, короткий викид, залипання сигналу в константу
 * й відмову давача.
 *
 * Друк — через std::printf: у прошивці лінкується саме він, а iostream тягне
 * десятки кілобайтів, яких на дрібному МК просто немає.
 */
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <limits>
#include <span>

#include "edge/anomaly_detector.hpp"
#include "edge/telemetry_frame.hpp"

namespace {

constexpr std::uint32_t sample_count = 600;
constexpr std::uint32_t period_ms    = 10;

/// xorshift32 — детермінований шум: прогін відтворюваний до біта.
class Noise {
public:
    float next(float amplitude) noexcept
    {
        state_ ^= state_ << 13;
        state_ ^= state_ >> 17;
        state_ ^= state_ << 5;
        const float unit = static_cast<float>(state_ >> 8) / static_cast<float>(1u << 24);
        return (unit * 2.0f - 1.0f) * amplitude;
    }

private:
    std::uint32_t state_{0x1234ABCD};
};

/// Напруга мережі: 230 В із шумом 0.1 В — саме той випадок, на якому
/// наївна формула дисперсії втрачає значущі розряди.
float synth_sample(std::uint32_t k, Noise& noise) noexcept
{
    if (k == 420) {
        return std::numeric_limits<float>::quiet_NaN();   // обірваний вхід АЦП
    }
    if (k >= 300 && k < 305) {
        return 236.5f + noise.next(0.1f);                 // викид на ~6 В
    }
    if (k >= 500) {
        return 231.0f;                                    // залипання, сигма -> 0
    }
    const float drift = k > 200 ? 0.004f * static_cast<float>(k - 200) : 0.0f;
    return 230.0f + drift + noise.next(0.1f);
}

const char* action_name(edge::Action a) noexcept
{
    switch (a) {
        case edge::Action::Discard:      return "DISCARD";
        case edge::Action::Heartbeat:    return "HEARTBEAT";
        case edge::Action::AnomalyAlarm: return "ALARM";
    }
    return "?";
}

void print_frame(const edge::Report& report, std::span<const float> snapshot)
{
    edge::FrameStorage storage{};
    const auto frame = edge::encode(report, snapshot, std::span{storage});
    if (!frame) {
        std::printf("      кадр не спакувався\n");
        return;
    }

    std::printf("      кадр %zu Б (сирий знімок float зайняв би %zu Б), CRC 0x%04X:\n      ",
                frame->size(), snapshot.size() * sizeof(float),
                edge::crc16_ccitt(frame->first(frame->size() - 2)));

    std::size_t column = 0;
    for (const std::byte b : *frame) {
        std::printf("%02X", std::to_integer<unsigned>(b));
        if (++column % 24 == 0 && column < frame->size()) {
            std::printf("\n      ");
        }
    }
    std::printf("\n");
}

}  // namespace

int main()
{
    edge::AnomalyDetector detector{edge::Millis{0}};
    Noise noise;

    std::uint32_t transmitted = 0;
    std::uint32_t alarms = 0;

    for (std::uint32_t k = 0; k < sample_count; ++k) {
        const edge::Millis now{k * period_ms};
        const edge::Report report = detector.process(synth_sample(k, noise), now);
        if (report.action == edge::Action::Discard) {
            continue;
        }

        ++transmitted;
        if (report.action == edge::Action::AnomalyAlarm) {
            ++alarms;
        }

        std::printf("k=%3u  t=%5u мс  %-9s  x=%8.3f  mean=%8.3f  sigma=%6.4f  z=%5.2f%s\n",
                    k, now.count(), action_name(report.action),
                    static_cast<double>(report.value),
                    static_cast<double>(report.mean),
                    static_cast<double>(report.stddev),
                    static_cast<double>(report.z),
                    report.sensor_fault ? "  [відмова давача]" : "");

        if (report.action == edge::Action::AnomalyAlarm) {
            std::array<float, edge::snapshot_depth> buffer{};
            const std::size_t n = detector.snapshot(std::span{buffer});
            const std::span<const float> history{buffer.data(), n};

            if (!history.empty()) {
                std::printf("      передісторія %zu вибірок: %.3f ... %.3f\n",
                            history.size(),
                            static_cast<double>(history.front()),
                            static_cast<double>(history.back()));
            }
            print_frame(report, history);
        }
    }

    std::printf("\nВибірок: %u.  В ефір пішло: %u (%.1f%%), з них тривог: %u.\n",
                sample_count, transmitted,
                100.0 * transmitted / sample_count, alarms);
    return 0;
}
