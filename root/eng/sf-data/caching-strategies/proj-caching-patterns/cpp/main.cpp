#include <iostream>
#include <string>
#include <unordered_map>
#include <optional>
#include <mutex>
#include <shared_mutex>
#include <chrono>
#include <thread>
#include <condition_variable>
#include <vector>
#include <memory>
#include <functional>
#include <future>

// ── Інтерфейс первинного надійного сховища ──────────────────────────────────
class Database {
public:
    virtual ~Database() = default;
    virtual std::optional<std::string> get(const std::string& key) = 0;
    virtual void set(const std::string& key, const std::string& value) = 0;
    virtual void batch_set(const std::vector<std::pair<std::string, std::string>>& items) = 0;
};

// Імітація бази даних із затримками дискового вводу-виводу
class MockDatabase : public Database {
    mutable std::shared_mutex mtx_;
    std::unordered_map<std::string, std::string> storage_;
public:
    std::optional<std::string> get(const std::string& key) override {
        std::this_thread::sleep_for(std::chrono::milliseconds(10)); // імітація IO
        std::shared_lock lock(mtx_);
        auto it = storage_.find(key);
        if (it != storage_.end()) return it->second;
        return std::nullopt;
    }

    void set(const std::string& key, const std::string& value) override {
        std::this_thread::sleep_for(std::chrono::milliseconds(15)); // імітація fsync
        std::unique_lock lock(mtx_);
        storage_[key] = value;
    }

    void batch_set(const std::vector<std::pair<std::string, std::string>>& items) override {
        std::this_thread::sleep_for(std::chrono::milliseconds(25)); // груповий запис
        std::unique_lock lock(mtx_);
        for (const auto& [k, v] : items) {
            storage_[k] = v;
        }
    }
};

// ── Швидкий потокобезпечний кеш у пам'яті ──────────────────────────────────
class CacheStore {
    mutable std::shared_mutex mtx_;
    std::unordered_map<std::string, std::string> map_;
public:
    std::optional<std::string> get(const std::string& key) const {
        std::shared_lock lock(mtx_);
        auto it = map_.find(key);
        if (it != map_.end()) return it->second;
        return std::nullopt;
    }

    void set(const std::string& key, const std::string& value) {
        std::unique_lock lock(mtx_);
        map_[key] = value;
    }

    void del(const std::string& key) {
        std::unique_lock lock(mtx_);
        map_.erase(key);
    }
};

// ── Допоміжний механізм Singleflight (придушення дублікатів запитів) ───────
class SingleflightGroup {
    struct Call {
        std::shared_future<std::optional<std::string>> future;
    };
    std::mutex mtx_;
    std::unordered_map<std::string, std::shared_ptr<Call>> calls_;
public:
    template<typename Fn>
    std::optional<std::string> execute(const std::string& key, Fn&& fn) {
        std::shared_ptr<Call> call;
        {
            std::lock_guard lock(mtx_);
            auto it = calls_.find(key);
            if (it != calls_.end()) {
                call = it->second;
            } else {
                call = std::make_shared<Call>();
                auto task = std::make_shared<std::packaged_task<std::optional<std::string>()>>(std::forward<Fn>(fn));
                call->future = task->get_future().share();
                calls_[key] = call;
                std::thread([task]() { (*task)(); }).detach();
            }
        }

        auto result = call->future.get();

        {
            std::lock_guard lock(mtx_);
            calls_.erase(key);
        }

        return result;
    }
};

// ── 1. Патерн Cache-Aside (Оркестрація застосунком) ─────────────────────────
class CacheAsideManager {
    std::shared_ptr<Database> db_;
    std::shared_ptr<CacheStore> cache_;
public:
    CacheAsideManager(std::shared_ptr<Database> db, std::shared_ptr<CacheStore> cache)
        : db_(std::move(db)), cache_(std::move(cache)) {}

    std::optional<std::string> get(const std::string& key) {
        // 1. Спроба читання з кешу
        if (auto cached = cache_->get(key); cached.has_value()) {
            return cached; // влучання (hit)
        }

        // 2. Промах (miss) — звернення до джерела правди
        auto from_db = db_->get(key);
        if (from_db.has_value()) {
            // 3. Ліниве наповнення кешу отриманим значенням
            cache_->set(key, *from_db);
        }
        return from_db;
    }

    void update(const std::string& key, const std::string& value) {
        // 1. Спершу фіксуємо зміну в базі даних
        db_->set(key, value);
        // 2. Інвалідуємо кеш (видалення, а не перезапис, захищає від гонок запису)
        cache_->del(key);
    }
};

// ── 2. Патерн Read-Through з підтримкою Singleflight ────────────────────────
class ReadThroughManager {
    std::shared_ptr<Database> db_;
    std::shared_ptr<CacheStore> cache_;
    SingleflightGroup sf_;
public:
    ReadThroughManager(std::shared_ptr<Database> db, std::shared_ptr<CacheStore> cache)
        : db_(std::move(db)), cache_(std::move(cache)) {}

    std::optional<std::string> get(const std::string& key) {
        if (auto cached = cache_->get(key); cached.has_value()) {
            return cached;
        }

        // При промаху дедуплікуємо паралельні звернення до одного ключа
        return sf_.execute(key, [this, key]() -> std::optional<std::string> {
            // Подвійна перевірка (Double-checked locking pattern)
            if (auto cached = cache_->get(key); cached.has_value()) {
                return cached;
            }
            auto val = db_->get(key);
            if (val.has_value()) {
                cache_->set(key, *val);
            }
            return val;
        });
    }
};

// ── 3. Патерн Write-Through (Синхронний наскрізний запис) ───────────────────
class WriteThroughManager {
    std::shared_ptr<Database> db_;
    std::shared_ptr<CacheStore> cache_;
public:
    WriteThroughManager(std::shared_ptr<Database> db, std::shared_ptr<CacheStore> cache)
        : db_(std::move(db)), cache_(std::move(cache)) {}

    std::optional<std::string> get(const std::string& key) {
        if (auto cached = cache_->get(key); cached.has_value()) {
            return cached;
        }
        auto from_db = db_->get(key);
        if (from_db.has_value()) {
            cache_->set(key, *from_db);
        }
        return from_db;
    }

    void set(const std::string& key, const std::string& value) {
        // Синхронний наскрізний запис: спершу база, потім оновлення кешу
        db_->set(key, value);
        cache_->set(key, value);
    }
};

// ── 4. Патерн Write-Behind (Асинхронний запис із коалесценцією) ─────────────
class WriteBehindManager {
    std::shared_ptr<Database> db_;
    std::shared_ptr<CacheStore> cache_;

    std::mutex queue_mtx_;
    std::condition_variable cv_;
    std::unordered_map<std::string, std::string> write_buffer_; // мапа для коалесценції
    size_t max_buffer_size_{10000};
    bool stop_{false};
    std::jthread worker_;

    void worker_loop() {
        while (true) {
            std::unordered_map<std::string, std::string> batch;
            {
                std::unique_lock lock(queue_mtx_);
                // Чекаємо тайм-ауту скидання (50 мс) або сигналу зупинки/переповнення
                cv_.wait_for(lock, std::chrono::milliseconds(50), [this] {
                    return stop_ || write_buffer_.size() >= 50;
                });

                if (stop_ && write_buffer_.empty()) {
                    break;
                }

                batch.swap(write_buffer_); // атомарне вилучення накопиченої пачки
            }

            if (!batch.empty()) {
                std::vector<std::pair<std::string, std::string>> items(batch.begin(), batch.end());
                db_->batch_set(items); // груповий запис у базу
            }
        }
    }

public:
    WriteBehindManager(std::shared_ptr<Database> db, std::shared_ptr<CacheStore> cache)
        : db_(std::move(db)), cache_(std::move(cache)) {
        worker_ = std::jthread([this] { worker_loop(); });
    }

    ~WriteBehindManager() {
        {
            std::unique_lock lock(queue_mtx_);
            stop_ = true;
        }
        cv_.notify_all();
        // std::jthread автоматично виконає join() у своєму деструкторі
    }

    std::optional<std::string> get(const std::string& key) {
        if (auto cached = cache_->get(key); cached.has_value()) {
            return cached;
        }
        auto from_db = db_->get(key);
        if (from_db.has_value()) {
            cache_->set(key, *from_db);
        }
        return from_db;
    }

    bool set(const std::string& key, const std::string& value) {
        // Миттєвий запис у кеш для забезпечення читання щойно записаного (Read-Your-Writes)
        cache_->set(key, value);

        // Буферизація з контролем переповнення (Backpressure)
        std::unique_lock lock(queue_mtx_);
        if (write_buffer_.size() >= max_buffer_size_) {
            return false; // захист від вичерпання пам'яті
        }
        write_buffer_[key] = value; // коалесценція: повторний запис замінює старе значення
        if (write_buffer_.size() >= 50) {
            cv_.notify_one();
        }
        return true;
    }
};
