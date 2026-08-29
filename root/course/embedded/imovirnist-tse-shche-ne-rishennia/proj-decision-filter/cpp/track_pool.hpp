#pragma once

// Статичний пул фільтрів для супроводу кількох об'єктів одночасно.
// Розмір задано типом: пам'ять під усі треки існує від старту прошивки,
// динамічного виділення в контурі реального часу немає взагалі.

#include "decision_filter.hpp"

#include <array>
#include <cstddef>
#include <functional>
#include <optional>

enum class PoolError {
    Full,     // вільних слотів немає
    Unknown,  // такого треку в пулі немає
};

[[nodiscard]] constexpr std::string_view describe(PoolError error) noexcept {
    switch (error) {
        case PoolError::Full:    return "пул треків вичерпано";
        case PoolError::Unknown: return "трек у пулі відсутній";
    }
    return "невідома вада пулу";
}

template <std::size_t MaxObjects = 32>
class TrackerFilterPool {
public:
    using Filter = DecisionConfidenceFilter;
    using FilterRef = std::reference_wrapper<Filter>;

    [[nodiscard]] static std::expected<TrackerFilterPool, ConfigError>
    make(const Filter::Config& cfg) noexcept {
        if (auto ok = Filter::validate(cfg); !ok) {
            return std::unexpected(ok.error());
        }
        return TrackerFilterPool{cfg};
    }

    // Фільтр для треку: наявний або щойно заведений у вільному слоті.
    // Відмова — не дрібниця: мовчазна втрата треку в системі гальмування
    // коштує дорожче за пропущений кадр, тож викликач мусить її розібрати.
    [[nodiscard]] std::expected<FilterRef, PoolError> track(int track_id, Millis now) noexcept {
        if (auto slot = indexOf(track_id)) {
            return FilterRef{filters_[*slot]};
        }
        for (std::size_t i = 0; i < MaxObjects; ++i) {
            if (track_ids_[i].has_value()) {
                continue;
            }
            // Слот міг лишитися з історією попереднього треку — заводимо його
            // з нуля, інакше новий об'єкт успадкував би чужу тривогу.
            filters_[i] = Filter{cfg_, now};
            track_ids_[i] = track_id;
            return FilterRef{filters_[i]};
        }
        return std::unexpected(PoolError::Full);
    }

    [[nodiscard]] std::expected<FilterRef, PoolError> find(int track_id) noexcept {
        if (auto slot = indexOf(track_id)) {
            return FilterRef{filters_[*slot]};
        }
        return std::unexpected(PoolError::Unknown);
    }

    bool release(int track_id) noexcept {
        if (auto slot = indexOf(track_id)) {
            track_ids_[*slot].reset();
            return true;
        }
        return false;
    }

    // Прибрати треки, які не оновлювалися довше за timeout.
    std::size_t sweep(Millis timeout, Millis now) noexcept {
        std::size_t dropped = 0;
        for (std::size_t i = 0; i < MaxObjects; ++i) {
            if (track_ids_[i] && filters_[i].idleFor(now) >= timeout) {
                track_ids_[i].reset();
                ++dropped;
            }
        }
        return dropped;
    }

    // Зведена команда на виконавчі органи: тривога хоча б за одним треком —
    // тривога для всього апарата.
    [[nodiscard]] bool anyActive() const noexcept {
        for (std::size_t i = 0; i < MaxObjects; ++i) {
            if (track_ids_[i] && filters_[i].isActive()) {
                return true;
            }
        }
        return false;
    }

    template <typename Fn>
    void forEach(Fn&& fn) const {
        for (std::size_t i = 0; i < MaxObjects; ++i) {
            if (track_ids_[i]) {
                fn(*track_ids_[i], filters_[i]);
            }
        }
    }

    [[nodiscard]] std::size_t size() const noexcept {
        std::size_t used = 0;
        for (const auto& id : track_ids_) {
            used += id.has_value() ? 1U : 0U;
        }
        return used;
    }

    [[nodiscard]] static constexpr std::size_t capacity() noexcept { return MaxObjects; }

private:
    explicit TrackerFilterPool(const Filter::Config& cfg) noexcept : cfg_{cfg} {
        filters_.fill(Filter{cfg});
    }

    [[nodiscard]] std::optional<std::size_t> indexOf(int track_id) const noexcept {
        for (std::size_t i = 0; i < MaxObjects; ++i) {
            if (track_ids_[i] == track_id) {
                return i;
            }
        }
        return std::nullopt;
    }

    typename Filter::Config cfg_{};
    std::array<Filter, MaxObjects> filters_{};
    std::array<std::optional<int>, MaxObjects> track_ids_{};
};
