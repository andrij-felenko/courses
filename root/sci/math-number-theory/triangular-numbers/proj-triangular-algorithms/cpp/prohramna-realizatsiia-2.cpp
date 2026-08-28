#include <iostream>
#include <vector>
#include <cstdint>
#include <optional>
#include <cstddef>

namespace math {

template <std::size_t PowerOfTwoExponent = 4>
class TriangularProbingHashTable {
public:
    static constexpr std::size_t Size = std::size_t{1} << PowerOfTwoExponent;

    struct Entry {
        std::uint64_t key;
        std::uint32_t value;
        bool occupied{false};
    };

private:
    std::vector<Entry> table_{Size};

    static constexpr std::uint32_t hash_func(std::uint64_t key) noexcept {
        key = (key ^ (key >> 30)) * 0xbf58476d1ce4e5b9ULL;
        key = (key ^ (key >> 27)) * 0x94d049bb133111ebULL;
        return static_cast<std::uint32_t>(key ^ (key >> 31));
    }

public:
    bool insert(std::uint64_t key, std::uint32_t value) {
        const std::uint32_t base_hash = hash_func(key);

        for (std::size_t step = 0; step < Size; ++step) {
            const std::size_t tri_offset = step * (step + 1) / 2;
            const std::size_t slot = (base_hash + tri_offset) & (Size - 1);

            if (!table_[slot].occupied || table_[slot].key == key) {
                table_[slot] = {key, value, true};
                return true;
            }
        }
        return false;
    }

    std::optional<std::uint32_t> find(std::uint64_t key) const {
        const std::uint32_t base_hash = hash_func(key);

        for (std::size_t step = 0; step < Size; ++step) {
            const std::size_t tri_offset = step * (step + 1) / 2;
            const std::size_t slot = (base_hash + tri_offset) & (Size - 1);

            if (!table_[slot].occupied) {
                return std::nullopt;
            }
            if (table_[slot].key == key) {
                return table_[slot].value;
            }
        }
        return std::nullopt;
    }
};

} // namespace math
