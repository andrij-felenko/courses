#include <span>
#include <vector>
#include <cmath>
#include <algorithm>

struct DataPoint {
    double time;
    double value;
};

std::vector<DataPoint> lttbDownsample(std::span<const DataPoint> input, std::size_t threshold) {
    if (input.empty()) return {};
    if (threshold >= input.size() || threshold < 3) {
        return std::vector<DataPoint>(input.begin(), input.end());
    }

    std::vector<DataPoint> sampled;
    sampled.reserve(threshold);
    sampled.push_back(input.front());

    const double bucket_size = static_cast<double>(input.size() - 2) / static_cast<double>(threshold - 2);
    std::size_t a_idx = 0;

    for (std::size_t i = 0; i < threshold - 2; ++i) {
        const std::size_t curr_start = static_cast<std::size_t>(i * bucket_size) + 1;
        const std::size_t curr_end = std::min(static_cast<std::size_t>((i + 1) * bucket_size) + 1, input.size());

        const std::size_t next_start = std::min(static_cast<std::size_t>((i + 1) * bucket_size) + 1, input.size());
        const std::size_t next_end = std::min(static_cast<std::size_t>((i + 2) * bucket_size) + 1, input.size());

        double avg_t = 0.0;
        double avg_v = 0.0;
        const std::size_t next_count = next_end - next_start;

        if (next_count > 0) {
            for (std::size_t j = next_start; j < next_end; ++j) {
                avg_t += input[j].time;
                avg_v += input[j].value;
            }
            avg_t /= static_cast<double>(next_count);
            avg_v /= static_cast<double>(next_count);
        } else {
            avg_t = input.back().time;
            avg_v = input.back().value;
        }

        const double a_t = input[a_idx].time;
        const double a_v = input[a_idx].value;
        double max_area = -1.0;
        std::size_t max_idx = curr_start;

        for (std::size_t p = curr_start; p < curr_end; ++p) {
            const double p_t = input[p].time;
            const double p_v = input[p].value;
            const double area = std::abs((a_t - avg_t) * (p_v - a_v) - (a_t - p_t) * (avg_v - a_v));
            if (area > max_area) {
                max_area = area;
                max_idx = p;
            }
        }

        sampled.push_back(input[max_idx]);
        a_idx = max_idx;
    }

    sampled.push_back(input.back());
    return sampled;
}
