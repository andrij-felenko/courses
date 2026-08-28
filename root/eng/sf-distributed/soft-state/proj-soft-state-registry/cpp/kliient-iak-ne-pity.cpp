#include <chrono>
#include <cstdint>
#include <functional>
#include <random>
#include <string>
#include <thread>

// Зерно — від імені вузла, а не від годинника.
uint64_t seed_from(const std::string& node_id) {
    uint64_t h = 1469598103934665603ull;                       // FNV-1a, 64 біти
    for (unsigned char c : node_id) { h ^= c; h *= 1099511628211ull; }
    return h;
}

class Heartbeat {
public:
    Heartbeat(std::chrono::milliseconds period, uint64_t seed)
        : period_(period), rng_(seed), spread_(0.5, 1.5) {}

    // Кожен інтервал тягнеться заново: сталий зсув фази теж рознесе вузли,
    // але не врятує від збігу з іншим періодичним процесом у системі.
    std::chrono::milliseconds next_interval() {
        const double f = spread_(rng_);
        return std::chrono::milliseconds(
            static_cast<long long>(period_.count() * f));
    }

    void run(const std::function<void()>& send) {
        std::this_thread::sleep_for(next_interval());          // перший інтервал теж випадковий
        for (;;) {
            send();
            std::this_thread::sleep_for(next_interval());
        }
    }

private:
    std::chrono::milliseconds             period_;
    std::mt19937_64                       rng_;
    std::uniform_real_distribution<double> spread_;
};
