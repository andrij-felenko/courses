#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <algorithm>
#include <numbers>

class PhiAccrualFailureDetector {
public:
    explicit PhiAccrualFailureDetector(
        size_t window_size = 1000,
        double threshold = 8.0,
        double min_std_dev_sec = 0.05,
        double acceptable_heartbeat_pause_sec = 0.0
    ) : capacity_(std::max<size_t>(window_size, 10)),
        threshold_(threshold),
        min_std_dev_(min_std_dev_sec),
        acceptable_pause_(acceptable_heartbeat_pause_sec),
        history_(capacity_, 0.0) {}

    void heartbeat(std::chrono::duration<double> timestamp) noexcept {
        const double now = timestamp.count();
        if (last_timestamp_ > 0.0) {
            const double interval = now - last_timestamp_;
            if (interval > 0.0) {
                push_interval(interval);
            }
        }
        last_timestamp_ = now;
    }

    void heartbeat() noexcept {
        const auto now = std::chrono::steady_clock::now().time_since_epoch();
        heartbeat(std::chrono::duration<double>(now));
    }

    [[nodiscard]] double phi(std::chrono::duration<double> timestamp) const noexcept {
        if (last_timestamp_ <= 0.0) {
            return 0.0;
        }

        const double now = timestamp.count();
        const double diff = now - last_timestamp_ - acceptable_pause_;
        if (diff <= 0.0) {
            return 0.0;
        }

        double mean = 1.0;
        double std_dev = min_std_dev_;

        if (size_ >= 2) {
            mean = sum_ / static_cast<double>(size_);
            const double variance = (sum_sq_ / static_cast<double>(size_)) - (mean * mean);
            std_dev = std::max(std::sqrt(std::max(0.0, variance)), min_std_dev_);
        }

        const double y = (diff - mean) / std_dev;
        const double e = std::exp(-y * (1.5976 + 0.070566 * y * y));

        double p_later = (diff > mean) ? (e / (1.0 + e)) : (1.0 - (1.0 / (1.0 + e)));

        if (p_later <= 0.0) {
            // Асимптотичне обчислення при великих затримках для запобігання underflow
            const double z = (diff - mean) / (std_dev * std::numbers::sqrt2);
            if (z > 3.0) {
                return ((z * z + std::log(z) + 0.57236) / std::numbers::ln10) - 0.30103;
            }
            return 50.0;
        }

        const double val = -std::log10(p_later);
        return std::max(0.0, val);
    }

    [[nodiscard]] double phi() const noexcept {
        const auto now = std::chrono::steady_clock::now().time_since_epoch();
        return phi(std::chrono::duration<double>(now));
    }

    [[nodiscard]] bool is_available(std::chrono::duration<double> timestamp) const noexcept {
        return phi(timestamp) < threshold_;
    }

    [[nodiscard]] bool is_available() const noexcept {
        return phi() < threshold_;
    }

    [[nodiscard]] double threshold() const noexcept { return threshold_; }

private:
    void push_interval(double interval) noexcept {
        if (size_ < capacity_) {
            history_[head_] = interval;
            sum_ += interval;
            sum_sq_ += interval * interval;
            ++size_;
        } else {
            const double old_val = history_[head_];
            sum_ = sum_ - old_val + interval;
            sum_sq_ = sum_sq_ - (old_val * old_val) + (interval * interval);
            history_[head_] = interval;
        }
        head_ = (head_ + 1) % capacity_;
    }

    size_t capacity_;
    double threshold_;
    double min_std_dev_;
    double acceptable_pause_;

    std::vector<double> history_;
    size_t size_{0};
    size_t head_{0};
    double sum_{0.0};
    double sum_sq_{0.0};
    double last_timestamp_{0.0};
};

int main() {
    PhiAccrualFailureDetector detector(1000, 8.0, 0.05);

    double sim_time = 500.0;
    // Імітація регулярного пульсу (T = 1.0 с)
    for (int i = 0; i < 50; ++i) {
        sim_time += 1.0 + (i % 3 - 1) * 0.01;
        detector.heartbeat(std::chrono::duration<double>(sim_time));
    }

    std::cout << "Аналіз стану після 50 сигналів пульсу:\n";
    for (double delay : {0.8, 1.0, 1.3, 1.8, 2.5}) {
        const auto check_time = std::chrono::duration<double>(sim_time + delay);
        const double current_phi = detector.phi(check_time);
        const bool alive = detector.is_available(check_time);

        std::cout << "Затримка " << delay << " с -> Phi = " 
                  << current_phi << " | Статус: " 
                  << (alive ? "ONLINE" : "OFFLINE (SUSPECTED)") << "\n";
    }

    return 0;
}
