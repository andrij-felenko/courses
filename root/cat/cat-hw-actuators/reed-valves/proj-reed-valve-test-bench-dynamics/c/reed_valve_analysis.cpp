#include <iostream>
#include <vector>
#include <numeric>
#include <cmath>
#include <algorithm>
#include <span>
#include <optional>

// Структура для зберігання параметрів вимірювань
struct Sample {
    uint32_t timestamp_ms;
    float pressure_upstream;
    float pressure_downstream;
    float optical_gate;
};

// Клас ковзного фільтра на базі std::vector
class MovingAverageFilter {
private:
    std::vector<float> buffer;
    size_t window_size;
    size_t index = 0;
    size_t count = 0;

public:
    explicit MovingAverageFilter(size_t window) : window_size(window), buffer(window, 0.0f) {}

    float update(float input) {
        buffer[index] = input;
        index = (index + 1) % window_size;
        if (count < window_size) {
            count++;
        }
        return std::accumulate(buffer.begin(), buffer.begin() + count, 0.0f) / count;
    }
};

// Функція пошуку переходу перепаду тиску через нуль із використанням std::optional
std::optional<uint32_t> detect_zero_crossing(float prev_dp, float curr_dp, uint32_t t) {
    if ((prev_dp < 0.0f && curr_dp >= 0.0f) || (prev_dp > 0.0f && curr_dp <= 0.0f)) {
        return t;
    }
    return std::nullopt;
}

// Функція аналізу буфера вимірювань за допомогою std::span
void analyze_valve_data(std::span<const Sample> samples) {
    MovingAverageFilter filter_up(5);
    MovingAverageFilter filter_down(5);
    MovingAverageFilter filter_opt(5);

    std::optional<uint32_t> zero_crossing_time;
    std::optional<uint32_t> valve_closure_time;

    float prev_dp = 0.0f;
    bool first = true;

    for (const auto& sample : samples) {
        float p_up_filtered = filter_up.update(sample.pressure_upstream);
        float p_down_filtered = filter_down.update(sample.pressure_downstream);
        float opt_filtered = filter_opt.update(sample.optical_gate);

        float curr_dp = p_up_filtered - p_down_filtered;

        if (!first && !zero_crossing_time) {
            zero_crossing_time = detect_zero_crossing(prev_dp, curr_dp, sample.timestamp_ms);
            if (zero_crossing_time) {
                std::cout << "[EVENT] C++ Zero crossing detected at t = " << *zero_crossing_time << " ms (dp = " << curr_dp << ")\n";
            }
        }

        if (!valve_closure_time && opt_filtered > 0.5f) {
            valve_closure_time = sample.timestamp_ms;
            std::cout << "[EVENT] C++ Valve closure detected at t = " << *valve_closure_time << " ms\n";
        }

        prev_dp = curr_dp;
        first = false;
    }

    if (zero_crossing_time && valve_closure_time) {
        int32_t delay_ms = static_cast<int32_t>(*valve_closure_time) - static_cast<int32_t>(*zero_crossing_time);
        std::cout << "\n[RESULT] C++ Pressure zero crossing: " << *zero_crossing_time << " ms\n";
        std::cout << "\n[RESULT] C++ Valve actual closure: " << *valve_closure_time << " ms\n";
        std::cout << "\n[RESULT] C++ Dynamic actuation delay: " << delay_ms << " ms\n";
    } else {
        std::cout << "\n[WARNING] C++ Could not determine complete actuation cycle.\n";
    }
}

int main() {
    std::cout << "=== Microfluidic Reed Valve Dynamic Analysis (C++) ===\n";

    constexpr size_t BUFFER_SIZE = 256;
    std::vector<Sample> raw_data(BUFFER_SIZE);

    for (size_t i = 0; i < BUFFER_SIZE; ++i) {
        raw_data[i].timestamp_ms = static_cast<uint32_t>(i * 2);
        float t_sec = i * 0.002f;
        raw_data[i].pressure_upstream = 50.0f * std::sin(2.0f * 3.14159f * 10.0f * t_sec);
        raw_data[i].pressure_downstream = 45.0f * std::sin(2.0f * 3.14159f * 10.0f * t_sec - 0.2f);
        raw_data[i].optical_gate = (t_sec > 0.05f && t_sec < 0.15f) ? 1.0f : 0.0f;
    }

    analyze_valve_data(raw_data);

    return 0;
}
