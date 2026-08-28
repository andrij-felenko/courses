#include <atomic>
#include <cstdint>
#include <mutex>
#include <string>
#include <unordered_map>
#include <chrono>

// Телеметрія одного застарілого шляху. Живе стільки, скільки вікно міграції.
class DeprecationMeter {
public:
    // Викликається на КОЖНЕ звернення до старого шляху — має бути дешевим.
    void record(const std::string& caller) {
        // Лічильник — гарячий шлях: лише атомарний інкремент, без замка.
        // relaxed достатньо: нам потрібна атомарність рахунку, а не
        // впорядкування щодо іншої пам'яті. На x86 це один LOCK XADD.
        hits_.fetch_add(1, std::memory_order_relaxed);

        // Реєстр «хто саме» — холодний бік: рідко читаємо, можна під замком.
        // Тут дані складніші за число, тож атоміком не обійтися.
        std::lock_guard<std::mutex> lk(mu_);
        Entry& e = callers_[caller];
        e.count += 1;
        e.last_seen = std::chrono::system_clock::now();
    }

    // Скільки разів старим шляхом скористалися за поточне вікно.
    uint64_t hits() const {
        return hits_.load(std::memory_order_relaxed);
    }

    // Знімок «хто ще ходить» — щоб піти й допомогти саме цим клієнтам перейти.
    struct Entry {
        uint64_t count = 0;
        std::chrono::system_clock::time_point last_seen{};
    };
    std::unordered_map<std::string, Entry> snapshot() const {
        std::lock_guard<std::mutex> lk(mu_);
        return callers_;              // копія під замком — безпечно віддати назовні
    }

    // Обнулити на початку нового вікна вимірювання (напр. щодоби).
    void reset() {
        hits_.store(0, std::memory_order_relaxed);
        std::lock_guard<std::mutex> lk(mu_);
        callers_.clear();
    }

private:
    std::atomic<uint64_t> hits_{0};
    mutable std::mutex mu_;
    std::unordered_map<std::string, Entry> callers_;
};
