// Реєстр наземних станцій. У C це пара stations.c/.h; тут значенневий тип із
// фіксованим std::array живе прямо в заголовку — окремій одиниці трансляції
// нічого було б робити.
#pragma once

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <optional>

namespace gcs {

// Час борта від старту. 64 біти chrono знімають ту саму проблему, заради якої
// у C доводилося порівнювати мілісекунди через різницю: переповнення немає.
using Millis = std::chrono::milliseconds;

enum class Role : std::uint8_t {
    Monitor   = 0x01,  // лише дивиться телеметрію
    Pilot     = 0x02,  // може претендувати на токен пілота
    Payload   = 0x04,  // камера, підвіс, скидання
    Commander = 0x08,  // аварійне перехоплення
};

// Набір ролей замість голого uint8_t: побітове «або» дозволене, довільна
// арифметика — ні.
class Roles {
public:
    constexpr Roles() noexcept = default;
    constexpr Roles(Role role) noexcept : bits_{static_cast<std::uint8_t>(role)} {}

    [[nodiscard]] constexpr bool has(Role role) const noexcept {
        return (bits_ & static_cast<std::uint8_t>(role)) != 0U;
    }
    constexpr Roles& operator|=(Roles other) noexcept {
        bits_ = static_cast<std::uint8_t>(bits_ | other.bits_);
        return *this;
    }
    [[nodiscard]] friend constexpr Roles operator|(Roles a, Roles b) noexcept { return a |= b; }
    [[nodiscard]] friend constexpr bool operator==(Roles, Roles) noexcept = default;

private:
    std::uint8_t bits_{0};
};

struct Station {
    std::uint8_t id{0};
    Roles        roles{};
    Millis       last_seen{0};
};

class StationTable {
public:
    static constexpr std::size_t kCapacity = 8;

    // Записати станцію або оновити її час і ролі.
    // false — усі вісім слотів зайняті, дев'ятого пульта борт не бачить.
    bool touch(std::uint8_t id, Roles roles, Millis now) noexcept {
        if (auto* slot = find_mutable(id)) {
            // Ролі перечитуємо з кожного heartbeat: станція могла перезапуститися
            // з іншим набором повноважень.
            slot->roles = roles;
            slot->last_seen = now;
            return true;
        }
        auto free_slot = std::ranges::find_if(slots_, [](const auto& s) { return !s.has_value(); });
        if (free_slot == slots_.end()) {
            return false;
        }
        *free_slot = Station{id, roles, now};
        return true;
    }

    [[nodiscard]] const Station* find(std::uint8_t id) const noexcept {
        auto it = std::ranges::find_if(
            slots_, [id](const auto& s) { return s.has_value() && s->id == id; });
        return it == slots_.end() ? nullptr : &it->value();
    }

    [[nodiscard]] bool alive(std::uint8_t id, Millis now, Millis lease) const noexcept {
        const Station* s = find(id);
        return s != nullptr && (now - s->last_seen) <= lease;
    }

    // Жива станція І має вказану роль — саме ця перевірка стоїть на вході
    // кожної привілейованої операції.
    [[nodiscard]] bool authorized(std::uint8_t id, Role role, Millis now, Millis lease) const noexcept {
        const Station* s = find(id);
        return s != nullptr && s->roles.has(role) && (now - s->last_seen) <= lease;
    }

    // Прибрати станції, що мовчать довше за ttl.
    void expire(Millis now, Millis ttl) noexcept {
        for (auto& slot : slots_) {
            if (slot && (now - slot->last_seen) > ttl) {
                slot.reset();
            }
        }
    }

private:
    Station* find_mutable(std::uint8_t id) noexcept {
        auto it = std::ranges::find_if(
            slots_, [id](const auto& s) { return s.has_value() && s->id == id; });
        return it == slots_.end() ? nullptr : &it->value();
    }

    std::array<std::optional<Station>, kCapacity> slots_{};
};

}  // namespace gcs
