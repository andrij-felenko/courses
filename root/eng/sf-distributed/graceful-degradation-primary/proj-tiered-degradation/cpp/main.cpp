#include <chrono>
#include <string_view>
#include <array>
#include <vector>
#include <span>
#include <future>
#include <thread>
#include <iostream>
#include <cstdint>

namespace resilience {

using namespace std::chrono_literals;

struct AggregatedResponse {
    uint64_t order_id{0};
    double price{0.0};
    bool price_is_stale{false};
    std::vector<std::string_view> recommendations;
    bool is_degraded{false};
    uint32_t degraded_mask{0};
};

class DegradationPipeline {
public:
    static constexpr std::array<std::string_view, 3> STATIC_FALLBACK_TOP{
        "item_default_bestseller_1",
        "item_default_bestseller_2",
        "item_default_bestseller_3"
    };

    static AggregatedResponse Execute(std::chrono::milliseconds hard_deadline,
                                      std::chrono::milliseconds t1_delay,
                                      std::chrono::milliseconds t2_delay) {
        const auto start_time = std::chrono::steady_clock::now();
        AggregatedResponse response{.order_id = 987654321};

        // 1. Асинхронний запуск незалежних задач scatter-gather
        auto tier1_future = std::async(std::launch::async, [t1_delay]() -> double {
            std::this_thread::sleep_for(t1_delay);
            return 499.99;
        });

        auto tier2_future = std::async(std::launch::async, [t2_delay]() -> std::vector<std::string_view> {
            std::this_thread::sleep_for(t2_delay);
            return {"ai_personalized_watch_v2", "ai_personalized_strap_black"};
        });

        // 2. Збір Tier-2 із раннім проактивним дедлайном (35 мс)
        const auto t2_threshold = 35ms;
        if (tier2_future.wait_until(start_time + t2_threshold) == std::future_status::ready) {
            response.recommendations = tier2_future.get();
        } else {
            // Проактивна деградація на детермінований O(1) статичний список
            response.is_degraded = true;
            response.degraded_mask |= (1 << 2);
            response.recommendations.assign(STATIC_FALLBACK_TOP.begin(), STATIC_FALLBACK_TOP.end());
        }

        // 3. Збір Tier-1 із бізнес-порогом (70 мс)
        const auto t1_threshold = 70ms;
        if (tier1_future.wait_until(start_time + t1_threshold) == std::future_status::ready) {
            response.price = tier1_future.get();
            response.price_is_stale = false;
        } else {
            // Деградація на локальний кеш зі статусом застарілості
            response.is_degraded = true;
            response.degraded_mask |= (1 << 1);
            response.price = 450.00; // Кешована резервна ціна
            response.price_is_stale = true;
        }

        return response;
    }
};

} // namespace resilience
