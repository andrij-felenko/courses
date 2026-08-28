#include <chrono>
#include <random>
#include <algorithm>

class BackoffCalculator {
public:
    static std::chrono::milliseconds calculateDelay(
        int attempt,
        std::chrono::milliseconds baseDelay = std::chrono::milliseconds(500),
        std::chrono::milliseconds maxDelay = std::chrono::milliseconds(30000))
    {
        attempt = std::clamp(attempt, 0, 10);
        auto expDelay = baseDelay * (1 << attempt);
        expDelay = std::min(expDelay, maxDelay);

        // Додаємо випадковий джитер для запобігання Thundering Herd
        thread_local std::mt19937 gen(std::random_device{}());
        std::uniform_int_distribution<int64_t> dist(0, expDelay.count() / 4);
        
        return expDelay + std::chrono::milliseconds(dist(gen));
    }
};
