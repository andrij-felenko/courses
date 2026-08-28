#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <atomic>
#include <thread>
#include <chrono>
#include <span>

struct Backend {
    std::string endpoint;
    uint32_t weight{100};
    bool is_healthy{true};
};

struct RouteRule {
    std::string path_prefix;
    std::vector<Backend> backends;
};

// Незмінний зліпок конфігурації (Immutable Snapshot)
class ConfigSnapshot {
public:
    explicit ConfigSnapshot(uint64_t version, std::vector<RouteRule> routes)
        : version_(version), routes_(std::move(routes)) {}

    [[nodiscard]] uint64_t version() const noexcept { return version_; }

    [[nodiscard]] std::string_view match_route(std::string_view request_path) const noexcept {
        for (const auto& route : routes_) {
            if (request_path.starts_with(route.path_prefix)) {
                for (const auto& backend : route.backends) {
                    if (backend.is_healthy) {
                        return backend.endpoint;
                    }
                }
            }
        }
        return "503_SERVICE_UNAVAILABLE";
    }

private:
    uint64_t version_;
    std::vector<RouteRule> routes_;
};

// Маршрутизатор із розділеними площинами
class DecoupledRouter {
public:
    DecoupledRouter() = default;

    // =========================================================================
    // ШВИДКИЙ ШЛЯХ (Data Plane): нуль м'ютексів, потокобезпечно через shared_ptr
    // =========================================================================
    [[nodiscard]] std::string_view route_request(std::string_view path) const noexcept {
        // std::atomic_load для std::shared_ptr є потокобезпечним (C++20 std::atomic<std::shared_ptr<T>>)
        std::shared_ptr<const ConfigSnapshot> snap = std::atomic_load_explicit(&active_config_, std::memory_order_acquire);
        if (!snap) [[unlikely]] {
            return "500_NO_CONFIG";
        }
        return snap->match_route(path);
    }

    // =========================================================================
    // КОНТУР УПРАВЛІННЯ (Control Plane): фонова підготовка та атомарна заміна
    // =========================================================================
    void update_topology(uint64_t new_version, std::vector<RouteRule> new_routes) {
        // 1. Створюємо новий незмінний об'єкт у пам'яті
        auto candidate = std::make_shared<const ConfigSnapshot>(new_version, std::move(new_routes));

        // 2. Атомарно замінюємо покажчик з бар'єром пам'яті release-acquire
        std::atomic_store_explicit(&active_config_, candidate, std::memory_order_release);

        std::cout << "[Control Plane C++] Успішно оновлено конфігурацію до версії v" 
                  << new_version << "\n";
    }

private:
    std::shared_ptr<const ConfigSnapshot> active_config_{nullptr};
};
