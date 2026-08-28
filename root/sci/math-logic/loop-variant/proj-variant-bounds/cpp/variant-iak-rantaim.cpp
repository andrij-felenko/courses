#include <optional>
#include <utility>
#include <cassert>
#include <cstddef>

// Строгий спад + дно + збіг із передбаченою межею.
template <class V>
class Variant {
    V floor_;
    std::optional<std::size_t> budget_;
    std::optional<V> prev_;
    std::size_t steps_ = 0;

public:
    explicit Variant(V floor, std::optional<std::size_t> budget = std::nullopt)
        : floor_(std::move(floor)), budget_(budget) {}

    // Викликати ПЕРШИМ рядком тіла циклу — жодна гілка не прослизне.
    void step(const V& now) {
        ++steps_;
        assert(now >= floor_ && "варіант пробив дно");
        assert((!prev_ || now < *prev_) && "варіант не впав");
        assert((!budget_ || steps_ <= *budget_) && "перевищено передбачену межу");
        prev_ = now;
    }
};
