#include <iostream>
#include <atomic>
#include <memory>
#include <string>

struct SystemConfig {
    int timeout_ms;
    int max_retries;
    std::string endpoint;
};

class LockFreeCOWConfig {
    std::atomic<std::shared_ptr<const SystemConfig>> config;

public:
    LockFreeCOWConfig(SystemConfig initial)
        : config(std::make_shared<const SystemConfig>(std::move(initial))) {}

    std::shared_ptr<const SystemConfig> get_config() const {
        return std::atomic_load(&config);
    }

    template <typename Modifier>
    void update_config(Modifier mod) {
        auto old_cfg = get_config();
        std::shared_ptr<const SystemConfig> new_cfg;
        do {
            auto copy = std::make_shared<SystemConfig>(*old_cfg);
            mod(*copy);
            new_cfg = copy;
        } while (!std::atomic_compare_exchange_weak(&config, &old_cfg, new_cfg));
    }
};

int main() {
    std::cout << "=== Lock-Free Copy-On-Write Config (C++) ===\n";
    LockFreeCOWConfig container({500, 3, "https://api.example.com"});

    auto cfg1 = container.get_config();
    std::cout << "Current: " << cfg1->endpoint << " (timeout=" << cfg1->timeout_ms << ")\n";

    container.update_config([](SystemConfig& cfg) {
        cfg.timeout_ms = 1500;
        cfg.max_retries = 5;
    });

    auto cfg2 = container.get_config();
    std::cout << "Updated: " << cfg2->endpoint << " (timeout=" << cfg2->timeout_ms << ")\n";

    return 0;
}
