#pragma once

#include <array>
#include <atomic>
#include <cstdint>
#include <optional>
#include <type_traits>

namespace flight::control {

/* Поштова скринька на один кадр: пише обробник переривання UART/DMA, читає
   польотний цикл. М'ютекса тут бути не може — цикл не має права стати на замок,
   узятий перериванням, а переривання не має права чекати взагалі. Тому подвійний
   буфер (ping-pong): ISR заповнює тіньовий слот і атомарно перемикає індекс. */
template <typename T>
class Mailbox {
    static_assert(std::is_trivially_copyable_v<T>,
                  "кадр копіюється з переривання — тільки тривіальний тип");
    static_assert(std::atomic<std::uint32_t>::is_always_lock_free,
                  "на цій платформі лічильник не безблокувальний — скринька марна");

public:
    // Виклик із переривання: жодних циклів очікування — записали тінь, перемкнули.
    void publish(const T& value) noexcept {
        const unsigned back = front_.load(std::memory_order_relaxed) ^ 1u;
        slot_[back] = value;
        /* release: усе, записане вище, стає видно тому, хто прочитає з acquire.
           Спершу індекс, потім лічильник — щоб «новий кадр є» ніколи не
           випередило самого кадру. */
        front_.store(back, std::memory_order_release);
        seq_.fetch_add(1, std::memory_order_release);
    }

    // Виклик із польотного циклу: порожньо — цього такту джерело мовчить.
    [[nodiscard]] std::optional<T> take() noexcept {
        for (int attempt = 0; attempt < kRetries; ++attempt) {
            const auto before = seq_.load(std::memory_order_acquire);
            if (before == seen_)
                return std::nullopt;

            const unsigned index = front_.load(std::memory_order_acquire);
            T copy = slot_[index];

            /* Двох слотів мало, якщо переривання встигне опублікувати ДВІЧІ,
               поки ми копіюємо: другий кадр ляже саме в той слот, який читаємо.
               Ловимо це лічильником публікацій — він росте з кожним кадром. */
            if (seq_.load(std::memory_order_acquire) != before) {
                ++torn_;
                continue;
            }

            dropped_ += before - seen_ - 1;  // скільки кадрів цикл проспав
            seen_ = before;
            return copy;
        }
        /* Джерело сипле швидше, ніж цикл читає: візьмемо наступного такту.
           Серце джерела при цьому не б'ється — і сторож це побачить. */
        return std::nullopt;
    }

    [[nodiscard]] std::uint32_t dropped() const noexcept { return dropped_; }
    [[nodiscard]] std::uint32_t torn() const noexcept { return torn_; }

private:
    static constexpr int kRetries = 3;

    std::array<T, 2> slot_{};
    std::atomic<std::uint32_t> seq_{0};
    std::atomic<unsigned> front_{0};
    std::uint32_t seen_{0};    // поля нижче — тільки для споживача, без атомів
    std::uint32_t dropped_{0};
    std::uint32_t torn_{0};
};

}  // namespace flight::control
