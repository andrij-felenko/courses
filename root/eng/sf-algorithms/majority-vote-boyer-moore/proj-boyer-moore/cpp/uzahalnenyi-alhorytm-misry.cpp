#include <array>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

template <std::equality_comparable T, std::size_t K>
    requires (K >= 2)
class MisraGriesHeavyHitters {
public:
    static constexpr std::size_t SlotCount = K - 1;

    constexpr MisraGriesHeavyHitters() noexcept {
        for (auto& slot : slots_) {
            slot.count = 0;
        }
    }

    constexpr void update(const T& item) noexcept {
        // 1. Пошук чи елемент вже відслідковується
        for (auto& slot : slots_) {
            if (slot.count > 0 && slot.candidate == item) {
                ++slot.count;
                return;
            }
        }

        // 2. Пошук вільного слота
        for (auto& slot : slots_) {
            if (slot.count == 0) {
                slot.candidate = item;
                slot.count = 1;
                return;
            }
        }

        // 3. Групове скорочення лічильників усіх кандидатів
        for (auto& slot : slots_) {
            --slot.count;
        }
    }

    [[nodiscard]] std::vector<T> candidates() const {
        std::vector<T> result;
        result.reserve(SlotCount);
        for (const auto& slot : slots_) {
            if (slot.count > 0) {
                result.push_back(slot.candidate);
            }
        }
        return result;
    }

private:
    struct Slot {
        T candidate{};
        std::size_t count{0};
    };

    std::array<Slot, SlotCount> slots_{};
};
