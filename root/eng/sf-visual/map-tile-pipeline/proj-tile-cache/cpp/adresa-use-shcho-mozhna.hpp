#include <algorithm>
#include <atomic>
#include <cassert>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <memory>
#include <mutex>
#include <queue>
#include <unordered_map>
#include <unordered_set>
#include <vector>

// Адреса тайла. variant — усе, що робить два тайли з тими самими z/x/y
// різними картинками: джерело, стиль, щільність, мова підписів.
struct TileId {
    int32_t  z = 0;
    int32_t  x = 0;
    int32_t  y = 0;
    uint32_t variant = 0;

    // Сітки вкладені, тому предок — це зсув, а не пошук.
    constexpr TileId parent() const noexcept {
        return TileId{ z - 1, x >> 1, y >> 1, variant };
    }
    constexpr TileId ancestor(int32_t up) const noexcept {
        return TileId{ z - up, x >> up, y >> up, variant };
    }
    // Який із чотирьох квадрантів предка займає цей тайл: 0…3.
    // Саме це число каже, яку чверть предка розтягувати на місце діри.
    constexpr int quadrant() const noexcept {
        return int(((y & 1) << 1) | (x & 1));
    }
    // Уся адреса в одному 64-бітному числі: z 6 біт, x і y по 24, variant 10.
    // Межі: z ≤ 24 (звідси x, y < 2²⁴) і variant < 1024 — з запасом
    // на будь-яку карту, яку віддає тайл-сервер.
    constexpr uint64_t key() const noexcept {
        return (uint64_t(uint32_t(z)) << 58)
             | (uint64_t(uint32_t(x)) << 34)
             | (uint64_t(uint32_t(y)) << 10)
             |  uint64_t(variant & 0x3FFu);
    }
};

constexpr bool operator==(const TileId& a, const TileId& b) noexcept {
    return a.key() == b.key();
}

// Карта замикається по довготі: тайл «за правим краєм світу» — це тайл
// біля лівого. Нормалізують ДО створення TileId: від'ємний x дав би
// і неправильний зсув у parent(), і чужий ключ у кеші.
constexpr int32_t wrapX(int32_t x, int32_t z) noexcept {
    const int32_t n = int32_t(1) << z;
    return ((x % n) + n) % n;
}

struct TileHash {
    size_t operator()(const TileId& t) const noexcept {
        uint64_t k = t.key();                        // фіналізатор splitmix64
        k ^= k >> 30;  k *= 0xbf58476d1ce4e5b9ull;
        k ^= k >> 27;  k *= 0x94d049bb133111ebull;
        k ^= k >> 31;
        return size_t(k);
    }
};
