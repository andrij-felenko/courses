#include <cstdint>
#include <vector>
#include <span>
#include <algorithm>

#if defined(__x86_64__) || defined(_M_X64)
#include <immintrin.h>
#define HAS_BMI2 1
#endif

namespace spatial {

class Morton2D {
public:
    static constexpr uint64_t spread_bits(uint32_t v) noexcept {
        uint64_t x = v & 0xFFFFFFFFULL;
        x = (x | (x << 16)) & 0x0000FFFF0000FFFFULL;
        x = (x | (x <<  8)) & 0x00FF00FF00FF00FFULL;
        x = (x | (x <<  4)) & 0x0F0F0F0F0F0F0F0FULL;
        x = (x | (x <<  2)) & 0x3333333333333333ULL;
        x = (x | (x <<  1)) & 0x5555555555555555ULL;
        return x;
    }

    static uint64_t encode(uint32_t x, uint32_t y) noexcept {
#if defined(HAS_BMI2)
        return _pdep_u64(x, 0x5555555555555555ULL) |
               _pdep_u64(y, 0xAAAAAAAAAAAAAAAAULL);
#else
        return spread_bits(x) | (spread_bits(y) << 1);
#endif
    }
};

struct Point2D {
    uint32_t x{0}, y{0};
    uint64_t key{0};

    Point2D() = default;
    Point2D(uint32_t px, uint32_t py)
        : x(px), y(py), key(Morton2D::encode(px, py)) {}

    bool operator<(const Point2D& other) const noexcept {
        return key < other.key;
    }
};

struct BoundingBox2D {
    uint32_t min_x, max_x;
    uint32_t min_y, max_y;

    [[nodiscard]] bool contains(uint32_t px, uint32_t py) const noexcept {
        return px >= min_x && px <= max_x && py >= min_y && py <= max_y;
    }

    [[nodiscard]] std::pair<uint64_t, uint64_t> key_range() const noexcept {
        return {Morton2D::encode(min_x, min_y), Morton2D::encode(max_x, max_y)};
    }
};

class MortonIndex2D {
public:
    explicit MortonIndex2D(std::vector<Point2D> points)
        : points_(std::move(points)) {
        std::sort(points_.begin(), points_.end());
    }

    [[nodiscard]] std::vector<Point2D> query_range(const BoundingBox2D& box) const {
        std::vector<Point2D> result;
        auto [min_key, max_key] = box.key_range();

        // Двійковий пошук точки старту O(log N)
        auto it = std::lower_bound(points_.begin(), points_.end(), min_key,
            [](const Point2D& pt, uint64_t target_key) {
                return pt.key < target_key;
            });

        for (; it != points_.end() && it->key <= max_key; ++it) {
            if (box.contains(it->x, it->y)) {
                result.push_back(*it);
            }
        }
        return result;
    }

private:
    std::vector<Point2D> points_;
};

} // namespace spatial
