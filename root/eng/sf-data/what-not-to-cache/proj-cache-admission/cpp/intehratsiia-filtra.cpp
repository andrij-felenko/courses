#include <string_view>
#include <string>
#include <functional>
#include <optional>
#include <iostream>

class SmartCacheClient {
public:
    SmartCacheClient() = default;

    template <typename DbFetchFn>
    [[nodiscard]] std::optional<std::string> get_or_load(
        std::string_view key,
        DbFetchFn&& db_fetch) noexcept 
    {
        // 1. Фіксуємо звернення в локальному пам'яттєвому ескізі
        admission_filter_.record_access(key);

        // 2. Спроба отримання з кешу
        if (auto cached = redis_get_stub(key); cached.has_value()) {
            return cached;
        }

        // 3. Промах: звернення до первинного сховища
        auto fresh_data = db_fetch(key);
        if (!fresh_data.has_value()) {
            return std::nullopt;
        }

        // 4. Перевірка допуску перед мережевим записом у Redis
        const uint8_t freq = admission_filter_.estimate_frequency(key);
        if (freq >= 2) {
            redis_set_stub(key, *fresh_data);
        }

        return fresh_data;
    }

private:
    TinyLfuAdmissionFilter admission_filter_{};

    static std::optional<std::string> redis_get_stub(std::string_view) noexcept {
        return std::nullopt; // Імітація промаху
    }

    static void redis_set_stub(std::string_view, std::string_view) noexcept {
        // Запис у віддалений Redis
    }
};
