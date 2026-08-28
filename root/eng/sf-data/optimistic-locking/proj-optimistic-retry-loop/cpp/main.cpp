#include <iostream>
#include <cstdint>
#include <random>
#include <chrono>
#include <thread>
#include <expected>
#include <functional>
#include <concepts>
#include <algorithm>

struct AccountRecord {
    uint64_t account_id{0};
    int64_t balance_cents{0};
    uint64_t version{0};
};

enum class TxError {
    NotFound,
    InsufficientFunds,
    ConcurrencyConflict,
    MaxRetriesExceeded,
    DatabaseError
};

struct RetryPolicy {
    uint32_t max_retries{5};
    std::chrono::milliseconds base_delay{10};
    std::chrono::milliseconds max_delay{200};
};

/* Інтерфейс репозиторію даних */
class MockAccountRepository {
public:
    explicit MockAccountRepository(uint64_t id, int64_t initial_balance)
        : record_{id, initial_balance, 1} {}

    [[nodiscard]] std::expected<AccountRecord, TxError> get_by_id(uint64_t id) const {
        if (record_.account_id != id) {
            return std::unexpected(TxError::NotFound);
        }
        return record_;
    }

    /* Атомарний CAS-запис */
    [[nodiscard]] std::expected<void, TxError> update_cas(uint64_t id, int64_t new_balance, uint64_t expected_version) {
        if (record_.account_id != id) {
            return std::unexpected(TxError::NotFound);
        }
        if (record_.version != expected_version) {
            return std::unexpected(TxError::ConcurrencyConflict); // affected_rows == 0
        }

        record_.balance_cents = new_balance;
        record_.version++;
        return {};
    }

private:
    AccountRecord record_;
};

/* Універсальний рандомізований генератор пауз (Full Jitter) */
class JitterBackoff {
public:
    explicit JitterBackoff(RetryPolicy policy)
        : policy_(policy), rng_(std::random_device{}()) {}

    void wait(uint32_t attempt) {
        uint64_t multiplier = 1ULL << std::min(attempt, 31u);
        auto calculated = policy_.base_delay * multiplier;
        auto capped = std::min(calculated, policy_.max_delay);

        std::uniform_int_distribution<uint64_t> dist(0, capped.count());
        auto actual_sleep = std::chrono::milliseconds(dist(rng_));
        
        std::this_thread::sleep_for(actual_sleep);
    }

private:
    RetryPolicy policy_;
    std::mt19937 rng_;
};

/* Узагальнений виконавець оптимістичних транзакцій */
template <typename TxFn>
auto execute_optimistic_retry(const RetryPolicy& policy, TxFn&& action)
    -> std::expected<typename std::invoke_result_t<TxFn>::value_type, TxError>
{
    JitterBackoff backoff(policy);

    for (uint32_t attempt = 0; attempt <= policy.max_retries; ++attempt) {
        auto result = action();
        if (result.has_value()) {
            return result.value();
        }

        // Якщо помилка не пов'язана з конкуренцією (наприклад, брак коштів) — не повторюємо
        if (result.error() != TxError::ConcurrencyConflict) {
            return std::unexpected(result.error());
        }

        if (attempt < policy.max_retries) {
            backoff.wait(attempt);
        }
    }

    return std::unexpected(TxError::MaxRetriesExceeded);
}

int main() {
    MockAccountRepository repo(42, 100000); // Баланс 100000 центів, версія 1
    RetryPolicy policy{.max_retries = 5, .base_delay = std::chrono::milliseconds(10), .max_delay = std::chrono::milliseconds(200)};

    uint64_t target_id = 42;
    int64_t withdraw_amount = 25000; // 25000 центів

    auto result = execute_optimistic_retry(policy, [&]() -> std::expected<AccountRecord, TxError> {
        // 1. Читання свіжого стану
        auto acc = repo.get_by_id(target_id);
        if (!acc) return std::unexpected(acc.error());

        // 2. Бізнес-перевірка
        if (acc->balance_cents < withdraw_amount) {
            return std::unexpected(TxError::InsufficientFunds);
        }

        // 3. Спроба фіксації
        int64_t new_balance = acc->balance_cents - withdraw_amount;
        auto update_res = repo.update_cas(target_id, new_balance, acc->version);
        if (!update_res) {
            return std::unexpected(update_res.error()); // ConcurrencyConflict
        }

        // Повертаємо оновлений об'єкт
        return AccountRecord{target_id, new_balance, acc->version + 1};
    });

    if (result.has_value()) {
        std::cout << "Транзакція успішна! Новий баланс: " << result->balance_cents 
                  << ", версія: " << result->version << '\n';
    } else {
        std::cerr << "Помилка транзакції, код: " << static_cast<int>(result.error()) << '\n';
    }

    return 0;
}
