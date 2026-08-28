#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <optional>
#include <cstdint>
#include <mutex>

namespace distributed {

// ── 1. Результати операцій ──────────────────────────────────────────────────
enum class FencingStatus {
    Accepted,
    RejectedStaleToken
};

struct LockGrant {
    bool        granted{false};
    uint64_t    fencing_token{0};
    std::chrono::milliseconds ttl{0};
};

// ── 2. Координатор блокувань ────────────────────────────────────────────────
class LockCoordinator {
public:
    LockGrant acquire(std::string_view client_id, std::chrono::milliseconds ttl) {
        std::unique_lock lock(mutex_);
        auto now = std::chrono::steady_clock::now();

        if (owner_.empty() || now >= lease_deadline_) {
            current_token_ = ++token_counter_; // Монотонне зростання епохи
            owner_ = client_id;
            lease_deadline_ = now + ttl;

            std::cout << "[КООРДИНАТОР] Замок надано '" << client_id
                      << "' | Токен: " << current_token_
                      << " | TTL: " << ttl.count() << " мс\n";

            return LockGrant{
                .granted = true,
                .fencing_token = current_token_,
                .ttl = ttl
            };
        }

        auto remaining = std::chrono::duration_cast<std::chrono::milliseconds>(lease_deadline_ - now);
        std::cout << "[КООРДИНАТОР] Відмова для '" << client_id
                  << "': зайнято '" << owner_ << "' (ще " << remaining.count() << " мс)\n";

        return LockGrant{.granted = false};
    }

private:
    std::mutex mutex_;
    std::string owner_;
    uint64_t current_token_{0};
    uint64_t token_counter_{0};
    std::chrono::steady_clock::time_point lease_deadline_{};
};

// ── 3. Захищене сховище даних ───────────────────────────────────────────────
class FencedStorage {
public:
    explicit FencedStorage(int64_t initial_balance)
        : balance_(initial_balance) {}

    FencingStatus write(std::string_view client_id, uint64_t token, int64_t new_balance) {
        std::unique_lock lock(mutex_);

        std::cout << "[СХОВИЩЕ] Запит від '" << client_id
                  << "' | Токен: " << token
                  << " | Новий баланс: $" << new_balance
                  << " | Найвищий відомий: " << highest_token_seen_ << "\n";

        if (token >= highest_token_seen_) {
            highest_token_seen_ = token;
            balance_ = new_balance;
            ++total_writes_;
            std::cout << "[СХОВИЩЕ] -> УСПІХ: токен " << token << " >= "
                      << highest_token_seen_ << ". Баланс = $" << balance_ << "\n";
            return FencingStatus::Accepted;
        }

        ++stale_rejections_;
        std::cout << "[СХОВИЩЕ] -> ВІДХИЛЕНО (ОГОРОЖА): токен " << token
                  << " < " << highest_token_seen_ << "! Застарілий запис відкинуто.\n";
        return FencingStatus::RejectedStaleToken;
    }

    [[nodiscard]] int64_t balance() const {
        std::unique_lock lock(mutex_);
        return balance_;
    }

    [[nodiscard]] uint64_t stale_rejections() const {
        std::unique_lock lock(mutex_);
        return stale_rejections_;
    }

private:
    mutable std::mutex mutex_;
    int64_t balance_{0};
    uint64_t highest_token_seen_{0};
    uint64_t total_writes_{0};
    uint64_t stale_rejections_{0};
};

} // namespace distributed

// ── 4. Запуск сценарію тестування ───────────────────────────────────────────
int main() {
    using namespace std::chrono_literals;

    distributed::LockCoordinator coordinator;
    distributed::FencedStorage storage(5000); // Початковий баланс: $5000

    std::cout << "=== СТАРТ СИМУЛЯЦІЇ РОЗПОДІЛЕНОЇ ОГОРОЖІ (C++) ===\n";
    std::cout << "Початковий баланс: $" << storage.balance() << "\n\n";

    // 1. Воркер A бере замок на 300 мс
    std::cout << "--- Крок 1: Воркер A бере замок ---\n";
    auto grant_a = coordinator.acquire("Worker-A", 300ms);
    if (!grant_a.granted) return 1;

    // 2. Воркер A планує списати $2000, але потрапляє в GC-паузу на 500 мс
    std::cout << "\n--- Крок 2: Воркер A засинає в GC-паузі на 500 мс (ліза 300 мс спливає) ---\n";
    int64_t prepared_a = storage.balance() - 2000;
    std::this_thread::sleep_for(500ms);

    // 3. Воркер B перехоплює замок після спливання лізи A
    std::cout << "\n--- Крок 3: Воркер B перехоплює замок ---\n";
    auto grant_b = coordinator.acquire("Worker-B", 300ms);
    if (!grant_b.granted) return 1;

    // 4. Воркер B успішно записує $6500 з токеном 2
    std::cout << "\n--- Крок 4: Воркер B записує баланс $6500 із токеном 2 ---\n";
    int64_t balance_b = storage.balance() + 1500;
    auto res_b = storage.write("Worker-B", grant_b.fencing_token, balance_b);
    if (res_b != distributed::FencingStatus::Accepted) return 1;

    // 5. Воркер A прокидається і надсилає застарілий запис $3000 з токеном 1
    std::cout << "\n--- Крок 5: Воркер A прокидається і надсилає запис із токеном 1 ---\n";
    auto res_a = storage.write("Worker-A", grant_a.fencing_token, prepared_a);

    // Підсумки
    std::cout << "\n=== ПІДСУМКИ ТЕСТУ ===\n";
    std::cout << "Фінальний баланс: $" << storage.balance() << " (Очікується: $6500)\n";
    std::cout << "Відхилено застарілих записів: " << storage.stale_rejections() << " (Очікується: 1)\n";

    if (storage.balance == 6500 && storage.stale_rejections == 1) {
        std::cout << ">>> РЕЗУЛЬТАТ: УСПІХ! Огорожа зберегла стан сховища. <<<\n";
    } else {
        std::cout << ">>> РЕЗУЛЬТАТ: ВАДА! Дані було пошкоджено. <<<\n";
    }

    return 0;
}
