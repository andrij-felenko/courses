// ack_set.hpp — множина квитованих номерів як кілька діапазонів.
//
// Навіщо множина, а не одне число «підтверджено до N».
//
// Вивантаження двоколійне. Свіжий кадр іде в ефір одразу, щойно ліг у
// флеш, і квитується десь угорі нумерації. Історія тим часом повзе від
// хвоста пачками. Тому квитанції приходять двома острівцями — біля
// хвоста й біля голови, — і одним числом їх не описати.
//
// Острівців тримаємо чотири: кожен розрив це один епізод втрати
// зв'язку. Коли місця бракує, найкоротший діапазон викидається, і ті
// кадри просто поїдуть удруге — сервер відкине дубль за номером.
//
// ⚠ Діапазони НІКОЛИ не розширюються заради місця: злити [10..12] і
// [20..22] у [10..22] означало б збрехати, що 13..19 доїхали, і тихо
// втратити сім кадрів.
#pragma once

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace sfq {

class AckSet {
public:
    static constexpr std::size_t kRanges = 4;

    struct Range {
        std::uint32_t lo{};  // включно
        std::uint32_t hi{};  // включно

        [[nodiscard]] constexpr std::uint32_t width() const noexcept { return hi - lo + 1; }
        [[nodiscard]] constexpr bool holds(std::uint32_t seq) const noexcept
        {
            return seq >= lo && seq <= hi;
        }
        // Сусідство рахуємо за суміжністю номерів: [4..7] і [8..9] — це
        // один суцільний шматок, і зливати їх чесно.
        [[nodiscard]] constexpr bool touches(const Range& other) const noexcept
        {
            return lo <= other.hi + 1 && other.lo <= hi + 1;
        }
    };

    void clear() noexcept
    {
        count_ = 0;
        dropped_ = 0;
    }

    // false — місця не було, найкоротший діапазон витіснено.
    bool add(Range range) noexcept
    {
        if (range.lo > range.hi) {
            return true;
        }

        // Поглинаємо все, що дотикається або перекривається.
        for (std::size_t i = 0; i < count_;) {
            if (ranges_[i].touches(range)) {
                range.lo = std::min(range.lo, ranges_[i].lo);
                range.hi = std::max(range.hi, ranges_[i].hi);
                erase_at(i);
                continue;  // після зсуву на цьому індексі вже інший діапазон
            }
            ++i;
        }

        bool full = false;
        if (count_ == kRanges) {
            evict_cheapest();
            full = true;
        }

        // Тримаємо впорядкованим — тоді holds і prune_below лишаються
        // лінійними без жодного сортування.
        const auto span = active();
        const auto pos = std::ranges::lower_bound(span, range.lo, {}, &Range::lo);
        insert_at(static_cast<std::size_t>(pos - span.begin()), range);
        return !full;
    }

    bool add(std::uint32_t seq) noexcept { return add(Range{seq, seq}); }

    [[nodiscard]] bool contains(std::uint32_t seq) const noexcept
    {
        return std::ranges::any_of(active(), [seq](const Range& r) { return r.holds(seq); });
    }

    // Усе, що вже нижче за хвіст, ні про що не свідчить, а місце в
    // таблиці потрібне.
    void prune_below(std::uint32_t seq) noexcept
    {
        for (std::size_t i = 0; i < count_;) {
            if (ranges_[i].hi < seq) {
                erase_at(i);
                continue;
            }
            ranges_[i].lo = std::max(ranges_[i].lo, seq);
            ++i;
        }
    }

    [[nodiscard]] std::span<const Range> active() const noexcept
    {
        return std::span{ranges_.data(), count_};
    }
    [[nodiscard]] std::uint32_t dropped() const noexcept { return dropped_; }

private:
    void erase_at(std::size_t idx) noexcept
    {
        for (std::size_t i = idx; i + 1 < count_; ++i) {
            ranges_[i] = ranges_[i + 1];
        }
        --count_;
    }

    void insert_at(std::size_t idx, Range range) noexcept
    {
        for (std::size_t i = count_; i > idx; --i) {
            ranges_[i] = ranges_[i - 1];
        }
        ranges_[idx] = range;
        ++count_;
    }

    // Викидаємо найкоротший: він коштує найменше повторних надсилань.
    void evict_cheapest() noexcept
    {
        const auto span = active();
        const auto victim = std::ranges::min_element(span, {}, &Range::width);
        erase_at(static_cast<std::size_t>(victim - span.begin()));
        ++dropped_;
    }

    [[nodiscard]] std::span<Range> active() noexcept { return std::span{ranges_.data(), count_}; }

    std::array<Range, kRanges> ranges_{};
    std::size_t count_{};
    std::uint32_t dropped_{};
};

}  // namespace sfq
