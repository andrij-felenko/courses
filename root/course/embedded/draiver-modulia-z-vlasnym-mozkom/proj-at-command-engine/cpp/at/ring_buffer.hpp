#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

#include "at/config.hpp"

namespace at {

/* Кільцевий буфер прийому UART DMA у циклічному режимі.

   Покажчика запису тут немає навіть як поля: він живе в апаратному регістрі
   DMA_CNDTR і обчислюється щоразу заново. Покажчик читання рухає лише
   парсер. Один власник на покажчик — і жодного вимкнення переривань. */
class RingBuffer {
public:
    struct Scan {
        enum class Outcome : std::uint8_t {
            Found,          // байт знайдено, index — його позиція
            Incomplete,     // до head байта немає, tail рухати НЕ можна
            LimitExceeded,  // ліміт вичерпано, index — куди викинути tail
        };
        Outcome outcome{Outcome::Incomplete};
        std::uint16_t index{0};
    };

    [[nodiscard]] std::span<std::uint8_t> dma_target() noexcept { return data_; }

    /* DMA_CNDTR рахує НЕДОпередані байти, тож покажчик запису — різниця. */
    [[nodiscard]] static constexpr std::uint16_t head_from_cndtr(std::uint16_t cndtr) noexcept
    {
        return static_cast<std::uint16_t>((config::kRxSize - cndtr) & config::kRxMask);
    }

    [[nodiscard]] std::uint16_t tail() const noexcept { return tail_; }

    [[nodiscard]] std::uint16_t available(std::uint16_t head) const noexcept
    {
        return static_cast<std::uint16_t>((head - tail_) & config::kRxMask);
    }

    /* Розвідка без споживання: шукає байт, не рухаючи tail. Саме тому URC,
       розірваний модулем на два кадри, не втрачається. */
    [[nodiscard]] Scan find(std::uint16_t head, std::uint8_t needle, std::size_t limit) const noexcept;

    /* Копіює [tail, stop) у out, викидаючи '\r', і зсуває tail за stop
       (тобто з'їдає ще й сам термінатор). Повертає, скільки записано. */
    std::size_t drain_to(std::uint16_t stop, std::span<char> out) noexcept;

    /* Шукає одиничний символ, який не завершується переводом рядка
       (запрошення '>'), і з'їдає все до нього включно. */
    bool take_upto(std::uint16_t head, std::uint8_t needle) noexcept;

    void seek(std::uint16_t index) noexcept { tail_ = static_cast<std::uint16_t>(index & config::kRxMask); }

    /* Викидає все прийняте: потрібно після таймауту, інакше хвіст
       напівприйнятої відповіді зсуне розбір наступної команди. */
    void flush(std::uint16_t head) noexcept { tail_ = head; }

private:
    std::array<std::uint8_t, config::kRxSize> data_{};
    std::uint16_t tail_{0};
};

}  // namespace at
