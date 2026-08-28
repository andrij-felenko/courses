#include <algorithm>
#include <array>
#include <bitset>
#include <chrono>
#include <cstdint>

enum class DedupVerdict { First, Copy, Stale, EpochReset, NoSlot };

class MultiBearerDedup {
public:
    using Clock = std::chrono::steady_clock;

    static constexpr std::size_t kWindow     = 256;   // глибина історії, пакетів
    static constexpr std::size_t kMaxSources = 8;
    static constexpr std::size_t kMaxBearers = 4;
    static constexpr auto        kIdle       = std::chrono::seconds{5};

    DedupVerdict check(std::uint32_t src_id, std::uint16_t epoch, std::uint32_t seq,
                       std::size_t bearer, Clock::time_point now) noexcept {
        Source* s = slot(src_id, now);
        if (s == nullptr) {
            return DedupVerdict::NoSlot;
        }
        s->last = now;

        // Перший пакет джерела або нова епоха після рестарту борту.
        if (!s->primed || s->epoch != epoch) {
            const bool was_primed = s->primed;
            s->epoch  = epoch;
            s->top    = seq;
            s->primed = true;
            s->seen.reset();
            s->seen.set(0);
            countFirst(bearer);
            return was_primed ? DedupVerdict::EpochReset : DedupVerdict::First;
        }

        const auto delta = static_cast<std::int32_t>(seq - s->top);

        if (delta > 0) {                                   // новий максимум
            s->seen <<= static_cast<std::size_t>(delta);   // зсув понад розмір
            s->seen.set(0);                                // std::bitset визначено
            s->top = seq;
            countFirst(bearer);
            return DedupVerdict::First;
        }

        const auto back = static_cast<std::size_t>(-delta);

        if (back >= kWindow) {
            countCopy(bearer);
            return DedupVerdict::Stale;
        }
        if (s->seen.test(back)) {
            countCopy(bearer);
            return DedupVerdict::Copy;
        }

        s->seen.set(back);                                 // запізніла, але перша
        countFirst(bearer);
        return DedupVerdict::First;
    }

    [[nodiscard]] std::uint32_t firstWins(std::size_t bearer) const noexcept {
        return bearer < kMaxBearers ? first_[bearer] : 0;
    }
    [[nodiscard]] std::uint32_t copies(std::size_t bearer) const noexcept {
        return bearer < kMaxBearers ? copies_[bearer] : 0;
    }

private:
    struct Source {
        std::uint32_t       id{};
        std::uint16_t       epoch{};
        std::uint32_t       top{};
        std::bitset<kWindow> seen{};     // біт k ↔ пакет top - k
        Clock::time_point   last{};
        bool                used{false};
        bool                primed{false};
    };

    Source* slot(std::uint32_t id, Clock::time_point now) noexcept {
        Source* spare = nullptr;
        for (Source& s : src_) {
            if (s.used && s.id == id) {
                return &s;
            }
            if (!s.used) {
                if (spare == nullptr) spare = &s;
            } else if (now - s.last > kIdle) {
                spare = &s;
            }
        }
        if (spare == nullptr) return nullptr;

        *spare = Source{};
        spare->id   = id;
        spare->used = true;
        return spare;
    }

    void countFirst(std::size_t b) noexcept { if (b < kMaxBearers) ++first_[b]; }
    void countCopy(std::size_t b)  noexcept { if (b < kMaxBearers) ++copies_[b]; }

    std::array<Source, kMaxSources>       src_{};
    std::array<std::uint32_t, kMaxBearers> first_{};
    std::array<std::uint32_t, kMaxBearers> copies_{};
};
