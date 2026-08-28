#include <iostream>
#include <chrono>
#include <random>
#include <cmath>
#include <algorithm>
#include <mutex>

class BackoffCalculator {
public:
    BackoffCalculator(std::chrono::duration<double> base, std::chrono::duration<double> max)
        : base_sec_(base.count()), max_sec_(max.count()), rng_(std::random_device{}()) {}

    std::chrono::duration<double> calculate(int attempt) {
        std::lock_guard<std::mutex> lock(mutex_);
        double temp = std::min(max_sec_, base_sec_ * std::pow(2.0, attempt));
        std::uniform_real_distribution<double> dist(0.0, temp);
        return std::chrono::duration<double>(dist(rng_));
    }

private:
    double base_sec_;
    double max_sec_;
    std::mt19937 rng_;
    std::mutex mutex_;
};

class AdmissionGate {
public:
    AdmissionGate(double rate_per_sec, double capacity)
        : rate_(rate_per_sec), capacity_(capacity), tokens_(capacity),
          last_update_(std::chrono::steady_clock::now()) {}

    bool allow() {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = std::chrono::steady_clock::now();
        std::chrono::duration<double> elapsed = now - last_update_;
        last_update_ = now;

        tokens_ = std::min(capacity_, tokens_ + elapsed.count() * rate_);
        if (tokens_ >= 1.0) {
            tokens_ -= 1.0;
            return true;
        }
        return false;
    }

private:
    double rate_;
    double capacity_;
    double tokens_;
    std::chrono::steady_clock::time_point last_update_;
    std::mutex mutex_;
};

int main() {
    BackoffCalculator backoff(std::chrono::milliseconds(100), std::chrono::seconds(10));
    AdmissionGate gate(50.0, 100.0);

    std::cout << "--- (C++) Розрахунок інтервалів Backoff з Full Jitter ---\n";
    for (int i = 0; i < 5; ++i) {
        auto delay = backoff.calculate(i);
        std::cout << "Спроба " << i << ": затримка " << delay.count() * 1000.0 << " мс\n";
    }

    int allowed = 0, rejected = 0;
    for (int i = 0; i < 120; ++i) {
        if (gate.allow()) {
            allowed++;
        } else {
            rejected++;
        }
    }
    std::cout << "Дозволено: " << allowed << ", Відхилено: " << rejected << "\n";

    return 0;
}
