#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <chrono>
#include <random>
#include <cmath>
#include <cstdint>
#include <optional>
#include <stdexcept>

// ── 1. Гешування FNV-1a (32 біти) ──────────────────────────────────────────
// Швидка некриптографічна геш-функція з відмінним лавинним ефектом для ключів
inline uint32_t fnv1a_32(std::string_view text) noexcept {
    uint32_t hash = 0x811c9dc5u;
    for (char c : text) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 0x01000193u;
    }
    return hash;
}

// ── 2. Структура кешованого запису зі статистикою для XFetch ───────────────
struct CacheItem {
    std::string value;
    std::chrono::steady_clock::time_point expiry; // запланований момент вичерпання TTL
    double compute_duration_sec{0.0};             // час (delta), витрачений СУБД на розрахунок
};

// ── 3. Кільце узгодженого гешування (Consistent Hash Ring) ──────────────────
class ConsistentHashRing {
public:
    explicit ConsistentHashRing(size_t vnodes_per_node = 150)
        : vnodes_per_node_(vnodes_per_node) {}

    // Додавання фізичного сервера: створює vnodes_per_node точок на кільці
    void add_node(const std::string& node_id) {
        std::lock_guard<std::mutex> lock(ring_mutex_);
        nodes_.push_back(node_id);
        for (size_t v = 0; v < vnodes_per_node_; ++v) {
            std::string vnode_key = node_id + "#vnode_" + std::to_string(v);
            uint32_t hash_point = fnv1a_32(vnode_key);
            ring_[hash_point] = node_id;
        }
    }

    // Видалення фізичного сервера: прибирає всі його віртуальні точки
    void remove_node(const std::string& node_id) {
        std::lock_guard<std::mutex> lock(ring_mutex_);
        std::erase(nodes_, node_id);
        for (size_t v = 0; v < vnodes_per_node_; ++v) {
            std::string vnode_key = node_id + "#vnode_" + std::to_string(v);
            uint32_t hash_point = fnv1a_32(vnode_key);
            ring_.erase(hash_point);
        }
    }

    // Пошук цільового сервера за ключем: рух за годинниковою стрілкою (O(log M))
    std::string get_node(std::string_view key) const {
        std::lock_guard<std::mutex> lock(ring_mutex_);
        if (ring_.empty()) {
            return "";
        }
        uint32_t key_hash = fnv1a_32(key);
        // Знаходимо перший вузол, чий хеш-поінт >= key_hash
        auto it = ring_.lower_bound(key_hash);
        if (it == ring_.end()) {
            it = ring_.begin(); // Замикання кільця (wrap-around до початкового сектора)
        }
        return it->second;
    }

    size_t total_vnodes() const {
        std::lock_guard<std::mutex> lock(ring_mutex_);
        return ring_.size();
    }

private:
    size_t vnodes_per_node_;
    std::vector<std::string> nodes_;
    std::map<uint32_t, std::string> ring_; // Червоно-чорне дерево: впорядкований простір точок
    mutable std::mutex ring_mutex_;
};

// ── 4. Координатор дедуплікації запитів (Singleflight Group) ────────────────
class SingleflightGroup {
public:
    using Result = std::string;

    // Гарантує, що для одного ключа функція fn() виконується лише одним потоком
    Result do_work(const std::string& key, std::function<Result()> fn) {
        std::unique_lock<std::mutex> lock(mutex_);

        auto it = in_flight_.find(key);
        if (it != in_flight_.end()) {
            // Запит на цей ключ уже виконується іншим воркером — підключаємося до очікування
            auto call = it->second;
            lock.unlock();

            std::unique_lock<std::mutex> call_lock(call->call_mutex);
            call->cv.wait(call_lock, [&call] { return call->done; });
            return call->val;
        }

        // Ми є першим потоком, що запросив ключ — реєструємо новий дескриптор виклику
        auto call = std::make_shared<Call>();
        in_flight_[key] = call;
        lock.unlock();

        // Виконуємо важку операцію (SQL-запит до СУБД) без утримання загального м'ютексу
        Result res;
        try {
            res = fn();
        } catch (...) {
            // При помилці сповіщаємо очікуючих і видаляємо виклик
            std::lock_guard<std::mutex> call_lock(call->call_mutex);
            call->done = true;
            call->cv.notify_all();
            lock.lock();
            in_flight_.erase(key);
            throw;
        }

        // Сповіщаємо всі підписані потоки, що чекають на результат
        {
            std::lock_guard<std::mutex> call_lock(call->call_mutex);
            call->val = res;
            call->done = true;
        }
        call->cv.notify_all();

        // Видаляємо дескриптор із реєстру активних викликів
        lock.lock();
        in_flight_.erase(key);
        return res;
    }

private:
    struct Call {
        std::mutex call_mutex;
        std::condition_variable cv;
        std::string val;
        bool done{false};
    };

    std::unordered_map<std::string, std::shared_ptr<Call>> in_flight_;
    std::mutex mutex_;
};

// ── 5. Клієнт розподіленого кешу (Resilient Distributed Cache Client) ───────
class ResilientCacheClient {
public:
    explicit ResilientCacheClient(ConsistentHashRing ring, double beta = 1.0)
        : ring_(std::move(ring)), beta_(beta), rng_(std::random_device{}()) {}

    // Метод Get-or-Compute: зчитує з кешу або атомарно обчислює у СУБД
    std::string get_or_compute(
        const std::string& key,
        std::chrono::seconds ttl,
        std::function<std::string()> db_loader
    ) {
        std::string target_node = ring_.get_node(key);
        auto now = std::chrono::steady_clock::now();

        // Крок 1. Спроба читання з кешу цільового шарду
        auto cached = read_from_shard(target_node, key);
        if (cached.has_value()) {
            // Перевіряємо умову стохастичного дострокового оновлення (алгоритм XFetch)
            if (!should_early_refresh(cached.value(), now)) {
                return cached.value().value; // Кеш свіжий і валідний — миттєве повернення (~1 мс)
            }
            // Якщо XFetch спрацював (TTL закінчується), запускаємо фоновий розрахунок через Singleflight
        }

        // Крок 2. Промах або дострокове оновлення — викликаємо Singleflight
        return singleflight_.do_work(key, [&]() -> std::string {
            // Повторна перевірка (Double-Checked Locking) всередині захищеної секції
            auto recheck = read_from_shard(target_node, key);
            if (recheck.has_value() && !should_early_refresh(recheck.value(), std::chrono::steady_clock::now())) {
                return recheck.value().value;
            }

            // Замір тривалості виконання запиту в СУБД (delta)
            auto start_t = std::chrono::steady_clock::now();
            std::string fresh_val = db_loader();
            auto end_t = std::chrono::steady_clock::now();

            double duration_sec = std::chrono::duration<double>(end_t - start_t).count();

            // Запис нового значення у шард
            CacheItem item{
                .value = fresh_val,
                .expiry = end_t + ttl,
                .compute_duration_sec = duration_sec
            };
            write_to_shard(target_node, key, item);
            return fresh_val;
        });
    }

private:
    // Алгоритм XFetch: перевірка now - beta * delta * ln(U) > expiry
    bool should_early_refresh(const CacheItem& item, std::chrono::steady_clock::time_point now) {
        if (now >= item.expiry) {
            return true; // Жорсткий промах: термін життя TTL повністю вичерпано
        }
        std::uniform_real_distribution<double> dist(0.0001, 0.9999);
        double u = dist(rng_);
        double delta = item.compute_duration_sec;
        double early_margin = -beta_ * delta * std::log(u);

        auto effective_time = now + std::chrono::duration<double>(early_margin);
        return effective_time >= item.expiry;
    }

    // Симуляція пам'яті віддалених серверів
    std::optional<CacheItem> read_from_shard(const std::string& node, const std::string& key) {
        std::lock_guard<std::mutex> lock(storage_mutex_);
        auto node_it = mock_storage_.find(node);
        if (node_it != mock_storage_.end()) {
            auto item_it = node_it->second.find(key);
            if (item_it != node_it->second.end()) {
                return item_it->second;
            }
        }
        return std::nullopt;
    }

    void write_to_shard(const std::string& node, const std::string& key, const CacheItem& item) {
        std::lock_guard<std::mutex> lock(storage_mutex_);
        mock_storage_[node][key] = item;
    }

    ConsistentHashRing ring_;
    SingleflightGroup singleflight_;
    double beta_;
    std::mt19937 rng_;
    std::unordered_map<std::string, std::unordered_map<std::string, CacheItem>> mock_storage_;
    std::mutex storage_mutex_;
};

int main() {
    ConsistentHashRing ring(100);
    ring.add_node("cache-node-01.internal:6379");
    ring.add_node("cache-node-02.internal:6379");
    ring.add_node("cache-node-03.internal:6379");

    ResilientCacheClient client(std::move(ring), 1.0);

    // Тестовий виклик читання з емуляцією затримки СУБД
    std::string user_data = client.get_or_compute("user:42:profile", std::chrono::seconds(60), []() {
        std::cout << "-> [СУБД] Виконання SQL-запиту SELECT * FROM users WHERE id = 42\n";
        return "{\"id\":42,\"name\":\"Alice\",\"status\":\"premium\"}";
    });

    std::cout << "<- Отримано результат: " << user_data << "\n";
    return 0;
}
