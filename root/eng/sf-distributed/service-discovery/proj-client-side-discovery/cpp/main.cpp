#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <shared_mutex>
#include <mutex>
#include <thread>
#include <chrono>
#include <random>
#include <memory>
#include <atomic>

/* Дескриптор екземпляра мікросервісу */
struct ServiceInstance {
    std::string id;
    std::string host;
    int port{0};
    int active_connections{0};
    bool is_healthy{true};
};

/* Потокобезпечний локальний кеш топології */
class ServiceDiscoveryCache {
public:
    void update(std::vector<ServiceInstance> new_instances, uint64_t revision) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        instances_ = std::move(new_instances);
        revision_ = revision;
    }

    /* Балансування навантаження за алгоритмом P2C */
    [[nodiscard]] std::optional<ServiceInstance> select_p2c() const {
        std::shared_lock<std::shared_mutex> lock(mutex_);

        if (instances_.empty()) {
            return std::nullopt;
        }

        if (instances_.size() == 1) {
            return instances_.front();
        }

        thread_local std::mt19937 gen(std::random_device{}());
        std::uniform_int_distribution<size_t> dist(0, instances_.size() - 1);

        size_t idx1 = dist(gen);
        size_t idx2 = dist(gen);
        while (idx2 == idx1 && instances_.size() > 1) {
            idx2 = dist(gen);
        }

        const auto& inst1 = instances_[idx1];
        const auto& inst2 = instances_[idx2];

        /* Обираємо екземпляр із меншим завантаженням */
        return (inst1.active_connections <= inst2.active_connections) ? inst1 : inst2;
    }

    [[nodiscard]] size_t size() const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        return instances_.size();
    }

    [[nodiscard]] uint64_t revision() const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        return revision_;
    }

private:
    mutable std::shared_mutex mutex_;
    std::vector<ServiceInstance> instances_;
    uint64_t revision_{0};
};

/* Імітація віддаленого реєстру сервісів */
class MockServiceRegistry {
public:
    void set_online(bool status) {
        std::lock_guard<std::mutex> lock(mutex_);
        online_ = status;
    }

    void set_instances(std::vector<ServiceInstance> instances, uint64_t revision) {
        std::lock_guard<std::mutex> lock(mutex_);
        db_ = std::move(instances);
        revision_ = revision;
    }

    struct FetchResult {
        std::vector<ServiceInstance> instances;
        uint64_t revision;
    };

    [[nodiscard]] std::optional<FetchResult> query_healthy(std::string_view service_name) const {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!online_) {
            return std::nullopt;
        }
        return FetchResult{db_, revision_};
    }

private:
    mutable std::mutex mutex_;
    std::vector<ServiceInstance> db_;
    uint64_t revision_{0};
    bool online_{true};
};

/* Клієнт виявлення з фоновим синхронізатором */
class ResilientDiscoveryClient {
public:
    explicit ResilientDiscoveryClient(std::shared_ptr<MockServiceRegistry> registry, std::string service_name)
        : registry_(std::move(registry)), service_name_(std::move(service_name)), running_(true) {
        worker_ = std::thread(&ResilientDiscoveryClient::sync_loop, this);
    }

    ~ResilientDiscoveryClient() {
        running_ = false;
        if (worker_.joinable()) {
            worker_.join();
        }
    }

    [[nodiscard]] std::optional<ServiceInstance> get_endpoint() const {
        return cache_.select_p2c();
    }

private:
    void sync_loop() {
        using namespace std::chrono_literals;

        while (running_) {
            auto result = registry_->query_healthy(service_name_);
            if (result.has_value()) {
                cache_.update(std::move(result->instances), result->revision);
                std::cout << "[Sync-Worker C++] Кеш оновлено: " << cache_.size()
                          << " інстансів (ревізія " << result->revision << ")\n";
            } else {
                std::cout << "[Sync-Worker C++] Реєстр недоступний. Використовуємо Stale Cache.\n";
            }
            std::this_thread::sleep_for(1000ms);
        }
    }

    std::shared_ptr<MockServiceRegistry> registry_;
    std::string service_name_;
    ServiceDiscoveryCache cache_;
    std::atomic<bool> running_{false};
    std::thread worker_;
};

int main() {
    auto registry = std::make_shared<MockServiceRegistry>();

    /* Початкове наповнення каталогу */
    registry->set_instances({
        {"payment-01", "10.0.1.10", 8080, 15, true},
        {"payment-02", "10.0.1.11", 8080, 2,  true}, // Найменше навантажений
        {"payment-03", "10.0.1.12", 8080, 28, true}
    }, 101);

    ResilientDiscoveryClient client(registry, "payment-service");

    /* Чекаємо запуску та первинного заповнення кешу */
    std::this_thread::sleep_for(std::chrono::milliseconds(1500));

    std::cout << "\n--- Розподіл викликів через клієнтське P2C-балансування ---\n";
    for (int i = 1; i <= 5; ++i) {
        if (auto endpoint = client.get_endpoint(); endpoint.has_value()) {
            std::cout << "Запит #" << i << " -> " << endpoint->id
                      << " (" << endpoint->host << ":" << endpoint->port
                      << "), активних з'єднань: " << endpoint->active_connections << "\n";
        }
    }

    /* Симуляція мережевого розділення / падіння реєстру */
    std::cout << "\n--- Симуляція відмови центрального реєстру ---\n";
    registry->set_online(false);
    std::this_thread::sleep_for(std::chrono::milliseconds(2000));

    std::cout << "\n--- Маршрутизація запитів під час відмови (Stale Routing) ---\n";
    for (int i = 1; i <= 3; ++i) {
        if (auto endpoint = client.get_endpoint(); endpoint.has_value()) {
            std::cout << "Stale-виклик #" << i << " -> " << endpoint->id
                      << " (" << endpoint->host << ":" << endpoint->port << ")\n";
        }
    }

    return 0;
}
