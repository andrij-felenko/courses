#include <cassert>
#include <cstdint>
#include <utility>
#include <vector>
#include "pc64.h"

template <class T>
class SparseNode {                     // до 64 логічних позицій
    std::uint64_t map_ = 0;
    std::vector<T> dense_;
public:
    bool has(unsigned i) const {
        assert(i < 64);
        return ((map_ >> i) & 1u) != 0;
    }
    unsigned slot(unsigned i) const {  // скільки зайнятих позицій перед i-ю
        assert(i < 64);
        return (unsigned)pc64(map_ & (((std::uint64_t)1 << i) - 1));
    }
    T *find(unsigned i) { return has(i) ? &dense_[slot(i)] : nullptr; }

    void set(unsigned i, T v) {
        unsigned s = slot(i);
        if (has(i)) { dense_[s] = std::move(v); return; }
        dense_.insert(dense_.begin() + s, std::move(v));
        map_ |= (std::uint64_t)1 << i;
    }
    std::size_t size() const { return dense_.size(); }
};
