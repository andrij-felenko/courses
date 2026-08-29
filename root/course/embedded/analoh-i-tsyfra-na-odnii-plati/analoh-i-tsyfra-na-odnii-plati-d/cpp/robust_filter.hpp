// robust_filter.hpp — ковзне усереднення з відкиданням викидів.
//
// Завади від перемикання цифрових шин не схожі на білий шум: це рідкі
// поодинокі стрибки в момент, коли мікроконтролер смикнув шину або пішов
// пакет по SPI. Просте середнє такий стрибок не прибирає, а розмазує по
// всьому вікну. Тому новий відлік спершу судимо за медіаною вікна і лише
// прийняті усереднюємо.
//
// Заголовок самодостатній: розмір вікна — параметр шаблону, стану поза
// об'єктом немає, динамічної пам'яті теж.
#pragma once

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <numeric>
#include <optional>
#include <span>

template <std::size_t Window = 16>
class RobustFilter {
    static_assert(Window >= 4, "медіана має сенс лише на вікні від чотирьох відліків");

public:
    struct Stats {
        std::uint32_t accepted{};
        std::uint32_t rejected{};
        // Розмах вікна «від краю до краю», у кодах перетворювача. Це та сама
        // величина, яку інженер бачить у терміналі як «молодші біти стрибають»,
        // і головний числовий вирок якості розведення плати.
        std::int32_t spread{};
        // Скільки розрядів із 24 несуть сигнал, а не шум.
        unsigned enob{};
    };

    // Повертає порожній optional, поки вікно наповнюється. Далі — середнє по
    // вікну; при відкинутому викиді середнє лишається попереднім, тобто
    // фільтр утримує останній достовірний рівень.
    std::optional<std::int32_t> push(std::int32_t code)
    {
        if (count_ == Window) {
            if (is_outlier(code)) {
                ++rejected_;
                ++streak_;

                if (streak_ < resync_after) {
                    return mean();
                }

                // Половина вікна поспіль «викиди» — це вже не завада, а
                // новий рівень сигналу (тензодавач навантажили). Скидаємо
                // вікно, інакше фільтр назавжди зачепився б за старе.
                head_ = 0;
                count_ = 0;
                streak_ = 0;
            } else {
                streak_ = 0;
            }
        }

        window_[head_] = code;
        head_ = (head_ + 1) % Window;
        if (count_ < Window) {
            ++count_;
        }
        ++accepted_;

        if (count_ < Window) {
            return std::nullopt;
        }
        return mean();
    }

    void reset() noexcept
    {
        window_.fill(0);
        head_ = 0;
        count_ = 0;
        streak_ = 0;
    }

    [[nodiscard]] std::span<const std::int32_t> window() const noexcept
    {
        return std::span<const std::int32_t>{window_.data(), count_};
    }

    [[nodiscard]] Stats stats() const noexcept
    {
        Stats s{.accepted = accepted_, .rejected = rejected_};

        if (count_ != 0) {
            const auto [lo, hi] = std::ranges::minmax(window());
            s.spread = hi - lo;
        }

        // 24 − ceil(log2(розмах + 1)); bit_width дає рівно цю величину.
        const auto noise_bits = std::bit_width(static_cast<std::uint32_t>(s.spread));
        s.enob = (noise_bits >= 24) ? 0u : 24u - noise_bits;

        return s;
    }

private:
    // Поріг «свій/чужий» = 3·σ, де σ оцінюємо через медіану модулів
    // відхилень: σ ≈ 1.4826·MAD. Множник 3·1.4826 = 4.4478 тримаємо в
    // тисячних, щоб не тягнути на мікроконтролер плаваючу кому.
    static constexpr std::int64_t mad_scale_num = 4448;
    static constexpr std::int64_t mad_scale_den = 1000;

    // Підлога порога, у кодах. На ідеально тихому вході MAD вироджується в
    // нуль — і без підлоги фільтр відкидав би геть усе, що не збіглося з
    // медіаною до останнього розряду.
    static constexpr std::int64_t mad_floor = 4;

    static constexpr std::size_t resync_after = Window / 2;

    static std::int32_t median_of(std::span<std::int32_t> values)
    {
        std::ranges::sort(values);

        const auto n = values.size();
        if (n % 2 != 0) {
            return values[n / 2];
        }
        return static_cast<std::int32_t>(
            (std::int64_t{values[n / 2 - 1]} + std::int64_t{values[n / 2]}) / 2);
    }

    [[nodiscard]] bool is_outlier(std::int32_t code) const
    {
        std::array<std::int32_t, Window> scratch{};

        std::ranges::copy(window(), scratch.begin());
        const std::int32_t median = median_of(std::span{scratch}.first(count_));

        std::ranges::transform(window(), scratch.begin(),
                               [median](std::int32_t v) { return std::abs(v - median); });
        const std::int32_t mad = median_of(std::span{scratch}.first(count_));

        // mad сягає мільйонів кодів, тож множення рахуємо в 64 бітах:
        // у 32 воно переповнилося б і поріг став би від'ємним.
        const std::int64_t threshold =
            std::max(mad_floor, (std::int64_t{mad} * mad_scale_num) / mad_scale_den);

        return std::abs(std::int64_t{code} - std::int64_t{median}) > threshold;
    }

    [[nodiscard]] std::int32_t mean() const noexcept
    {
        const std::int64_t sum = std::accumulate(window().begin(), window().end(), std::int64_t{0});
        return static_cast<std::int32_t>(sum / static_cast<std::int64_t>(count_));
    }

    std::array<std::int32_t, Window> window_{};
    std::size_t head_{0};
    std::size_t count_{0};
    std::size_t streak_{0};
    std::uint32_t accepted_{0};
    std::uint32_t rejected_{0};
};
