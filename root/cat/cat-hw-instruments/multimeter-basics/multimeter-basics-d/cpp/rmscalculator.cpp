#include <cmath>
#include <cstddef>
#include <cstdint>
#include <numeric>
#include <vector>

class RmsCalculator {
public:
    explicit RmsCalculator(float scale_factor) : scale_factor_(scale_factor) {}

    float computeTrueRms(const std::vector<int16_t>& samples) const {
        if (samples.empty()) return 0.0f;

        double sum_squares = std::accumulate(samples.begin(), samples.end(), 0.0,
            [this](double acc, int16_t raw_sample) {
                double voltage = static_cast<double>(raw_sample) * scale_factor_;
                return acc + (voltage * voltage);
            });

        return static_cast<float>(std::sqrt(sum_squares / static_cast<double>(samples.size())));
    }

private:
    float scale_factor_;
};
