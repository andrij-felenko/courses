#include <iostream>
#include <string>
#include <string_view>
#include <unordered_set>
#include <unordered_map>
#include <chrono>
#include <memory>
#include <expected>
#include <stdexcept>

// DTO вхідного повідомлення
struct PaymentMessage {
    std::string id;
    int64_t account_id;
    double amount;
};

// Можливі стани результату обробки
enum class ProcessingResult {
    Processed,
    DuplicateSkipped
};

// RAII обгортка для локальної транзакції бази даних
class DatabaseTransaction {
public:
    explicit DatabaseTransaction(bool &in_tx_flag) : in_tx_(in_tx_flag), committed_(false) {
        if (in_tx_) {
            throw std::runtime_error("Вкладені транзакції не підтримуються");
        }
        in_tx_ = true;
    }

    void commit() {
        committed_ = true;
    }

    ~DatabaseTransaction() noexcept {
        in_tx_ = false; // Якщо не було явного commit(), відбувається відкат
    }

    DatabaseTransaction(const DatabaseTransaction &) = delete;
    DatabaseTransaction &operator=(const DatabaseTransaction &) = delete;

private:
    bool &in_tx_;
    bool committed_;
};

// Імітація персистентного сховища з підтримкою транзакцій (L2)
class StorageEngine {
public:
    explicit StorageEngine(double initial_balance) : balance_(initial_balance), in_tx_(false) {}

    [[nodiscard]] double balance() const noexcept {
        return balance_;
    }

    [[nodiscard]] bool contains_inbox(std::string_view msg_id) const {
        return inbox_table_.contains(std::string(msg_id));
    }

    void insert_inbox(std::string_view msg_id) {
        inbox_table_.insert(std::string(msg_id));
    }

    void apply_balance_mutation(double delta) {
        balance_ += delta;
    }

    [[nodiscard]] DatabaseTransaction begin_transaction() {
        return DatabaseTransaction(in_tx_);
    }

private:
    double balance_;
    bool in_tx_;
    std::unordered_set<std::string> inbox_table_;
};

// Ковзне вікно дедуплікації в оперативній пам'яті (L1)
class SlidingWindowCache {
public:
    explicit SlidingWindowCache(std::chrono::seconds ttl) : ttl_(ttl) {}

    [[nodiscard]] bool contains(std::string_view key, std::chrono::steady_clock::time_point now) {
        cleanup(now);
        return cache_.contains(std::string(key));
    }

    void insert(std::string_view key, std::chrono::steady_clock::time_point now) {
        cache_[std::string(key)] = now;
    }

private:
    void cleanup(std::chrono::steady_clock::time_point now) {
        for (auto it = cache_.begin(); it != cache_.end();) {
            if (now - it->second > ttl_) {
                it = cache_.erase(it);
            } else {
                ++it;
            }
        }
    }

    std::chrono::seconds ttl_;
    std::unordered_map<std::string, std::chrono::steady_clock::time_point> cache_;
};

// Стійкий споживач з Transactional Inbox
class ReliableConsumer {
public:
    ReliableConsumer(double initial_balance, std::chrono::seconds cache_ttl)
        : storage_(initial_balance), l1_cache_(cache_ttl) {}

    std::expected<ProcessingResult, std::string> process_message(const PaymentMessage &msg) {
        const auto now = std::chrono::steady_clock::now();

        // 1. Швидка перевірка в L1 кеші
        if (l1_cache_.contains(msg.id, now)) {
            return ProcessingResult::DuplicateSkipped;
        }

        try {
            // 2. Старт локальної ACID транзакції
            auto tx = storage_.begin_transaction();

            // 3. Перевірка дублювання в L2 Inbox таблиці
            if (storage_.contains_inbox(msg.id)) {
                l1_cache_.insert(msg.id, now);
                return ProcessingResult::DuplicateSkipped;
            }

            // 4. Бізнес-дія: нарахування/списання балансу
            storage_.apply_balance_mutation(msg.amount);

            // 5. Запис ключа в Inbox у межах тієї ж транзакції
            storage_.insert_inbox(msg.id);

            // 6. Фіксація транзакції
            tx.commit();

            // 7. Оновлення L1 фільтра після успішної фіксації
            l1_cache_.insert(msg.id, now);

            return ProcessingResult::Processed;
        } catch (const std::exception &ex) {
            return std::unexpected(std::string("Помилка обробки транзакції: ") + ex.what());
        }
    }

    [[nodiscard]] double current_balance() const noexcept {
        return storage_.balance();
    }

private:
    StorageEngine storage_;
    SlidingWindowCache l1_cache_;
};

int main() {
    using namespace std::chrono_literals;

    ReliableConsumer consumer(1000.0, 300s); // 1000 грн початковий баланс, 300с TTL

    const PaymentMessage msg1{"tx_9981_order_44", 101, 250.0};
    const PaymentMessage duplicate{"tx_9981_order_44", 101, 250.0};
    const PaymentMessage msg2{"tx_9982_order_45", 101, 100.0};

    std::cout << "Початковий баланс: " << consumer.current_balance() << " грн\n";

    // Спроба 1: оригінальне повідомлення
    auto res1 = consumer.process_message(msg1);
    if (res1) {
        std::cout << "Спроба 1 (msg1): "
                  << (*res1 == ProcessingResult::Processed ? "ОБРОБЛЕНО" : "ДУБЛІКАТ")
                  << ", Баланс: " << consumer.current_balance() << " грн\n";
    }

    // Спроба 2: мережевий дублікат
    auto res_dup = consumer.process_message(duplicate);
    if (res_dup) {
        std::cout << "Спроба 2 (повтор msg1): "
                  << (*res_dup == ProcessingResult::Processed ? "ОБРОБЛЕНО" : "ДУБЛІКАТ (відсічено)")
                  << ", Баланс: " << consumer.current_balance() << " грн\n";
    }

    // Спроба 3: нове повідомлення
    auto res2 = consumer.process_message(msg2);
    if (res2) {
        std::cout << "Спроба 3 (msg2): "
                  << (*res2 == ProcessingResult::Processed ? "ОБРОБЛЕНО" : "ДУБЛІКАТ")
                  << ", Баланс: " << consumer.current_balance() << " грн\n";
    }

    return 0;
}
