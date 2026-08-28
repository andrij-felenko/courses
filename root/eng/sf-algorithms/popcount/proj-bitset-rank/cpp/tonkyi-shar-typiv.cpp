#include <cstddef>
#include <cstdint>
#include "bitset64.h"

template <std::size_t N>
class BitSet {
    static_assert(N > 0, "множина без жодного можливого елемента не має слів");
    static constexpr std::size_t W = BS_WORDS(N);
    std::uint64_t w_[W] = {};
public:
    void add(std::size_t i)               { bs_add(w_, i); }
    void del(std::size_t i)               { bs_del(w_, i); }
    bool has(std::size_t i) const         { return bs_has(w_, i) != 0; }
    void flip()                           { bs_flip(w_, N); }
    std::size_t count() const             { return bs_count(w_, W); }
    std::size_t rank(std::size_t i) const { return bs_rank(w_, i); }

    friend std::size_t intersection_count(const BitSet &a, const BitSet &b) {
        return bs_and_count(a.w_, b.w_, W);
    }
};
