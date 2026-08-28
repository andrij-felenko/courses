#include <array>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

namespace touch {

inline constexpr std::size_t kRows = 12, kCols = 8, kMaxTouches = 5;

struct Thresholds {
    std::int16_t finger_on  = 120;
    std::int16_t finger_off = 70;
    std::int16_t glove_on   = 35;
    std::int16_t self_gnd   = 60;
    std::int16_t base_slew  = 2;
};

enum class BlobKind { Finger, Water, Palm };

struct Blob {
    float       x{}, y{};          // центр у кроках сітки
    std::int32_t sum{};
    std::int16_t peak{};
    std::size_t  cells{};
    std::size_t  r_peak{}, c_peak{};
    BlobKind     kind{BlobKind::Finger};
};

template <class T>
using Grid = std::array<std::array<T, kCols>, kRows>;

class Engine {
public:
    explicit Engine(Thresholds t = {}) : thr_{t} {}

    // Один кадр: сира матриця + self-скани рядків і стовпців.
    std::vector<Blob> process(const Grid<std::int16_t>& raw,
                              std::span<const std::int16_t, kRows> self_row,
                              std::span<const std::int16_t, kCols> self_col)
    {
        self_row_ = self_row;
        self_col_ = self_col;
        computeDelta(raw);

        const std::int16_t on  = glove_ ? thr_.glove_on : thr_.finger_on;
        const std::int16_t off = glove_ ? std::int16_t(thr_.glove_on * 2 / 3)
                                        : thr_.finger_off;
        const std::int16_t gate = active_ ? off : on;

        Grid<bool> used{}, touched{};
        std::vector<Blob> touches;
        touches.reserve(kMaxTouches);
        bool weak_seen = false;

        for (std::size_t r = 0; r < kRows; ++r)
            for (std::size_t c = 0; c < kCols; ++c) {
                if (used[r][c] || delta_[r][c] < gate) {
                    if (!glove_ && delta_[r][c] >= thr_.glove_on)
                        weak_seen = true;
                    continue;
                }
                if (touches.size() == kMaxTouches) break;
                auto blob = grow(r, c, gate, used);
                if (!blob) continue;
                blob->kind = classify(*blob);
                if (blob->kind != BlobKind::Finger) continue;

                for (std::size_t rr = 0; rr < kRows; ++rr)
                    for (std::size_t cc = 0; cc < kCols; ++cc)
                        if (used[rr][cc]) touched[rr][cc] = true;

                touches.push_back(*blob);
            }

        updateGloveMode(touches, weak_seen);
        updateBaseline(touched);
        active_ = touches.size();
        return touches;
    }

private:
    void computeDelta(const Grid<std::int16_t>& raw)
    {
        for (std::size_t r = 0; r < kRows; ++r)
            for (std::size_t c = 0; c < kCols; ++c)
                delta_[r][c] = static_cast<std::int16_t>(baseline_[r][c] - raw[r][c]);
    }

    // Заливка по чотирьох сусідах; порожньо — коли пляма виродилася.
    std::optional<Blob> grow(std::size_t r0, std::size_t c0,
                             std::int16_t gate, Grid<bool>& used)
    {
        std::vector<std::pair<std::size_t, std::size_t>> stack{{r0, c0}};
        used[r0][c0] = true;

        Blob b{};
        std::int32_t wx = 0, wy = 0;

        while (!stack.empty() && b.cells < 64) {
            auto [r, c] = stack.back();
            stack.pop_back();
            const std::int16_t d = delta_[r][c];
            b.sum += d;
            wx += std::int32_t(d) * std::int32_t(c);
            wy += std::int32_t(d) * std::int32_t(r);
            if (d > b.peak) { b.peak = d; b.r_peak = r; b.c_peak = c; }
            ++b.cells;

            constexpr std::array<std::pair<int, int>, 4> kNb{
                {{-1, 0}, {1, 0}, {0, -1}, {0, 1}}};
            for (auto [dr, dc] : kNb) {
                const int nr = int(r) + dr, nc = int(c) + dc;
                if (nr < 0 || nc < 0 || nr >= int(kRows) || nc >= int(kCols)) continue;
                if (used[nr][nc] || delta_[nr][nc] < gate / 3) continue;
                used[nr][nc] = true;
                stack.emplace_back(std::size_t(nr), std::size_t(nc));
            }
        }
        if (b.sum <= 0) return std::nullopt;
        b.x = float(wx) / float(b.sum);
        b.y = float(wy) / float(b.sum);
        return b;
    }

    BlobKind classify(const Blob& b) const
    {
        const bool flat = std::int32_t(b.peak) * 16 < b.sum * 3;
        const bool grounded = self_row_[b.r_peak] > thr_.self_gnd &&
                              self_col_[b.c_peak] > thr_.self_gnd;
        if (!grounded) return BlobKind::Water;       // плаває — не палець
        if (flat && b.cells > 12) return BlobKind::Palm;
        return BlobKind::Finger;
    }

    void updateGloveMode(const std::vector<Blob>& touches, bool weak_seen)
    {
        if (touches.empty() && weak_seen) {
            if (++weak_streak_ >= 6) glove_ = true;
        } else {
            weak_streak_ = 0;
            if (!touches.empty() && touches.front().peak > thr_.finger_on * 2)
                glove_ = false;
        }
    }

    void updateBaseline(const Grid<bool>& touched)
    {
        for (std::size_t r = 0; r < kRows; ++r)
            for (std::size_t c = 0; c < kCols; ++c) {
                if (touched[r][c]) continue;          // під пальцем — ніколи
                const std::int16_t d = delta_[r][c];
                if (d > thr_.base_slew)       baseline_[r][c] -= thr_.base_slew;
                else if (d < -thr_.base_slew) baseline_[r][c] += thr_.base_slew;
                else                          baseline_[r][c] -= d;
            }
    }

    Thresholds thr_;
    Grid<std::int16_t> baseline_{}, delta_{};
    std::span<const std::int16_t, kRows> self_row_{};
    std::span<const std::int16_t, kCols> self_col_{};
    bool        glove_{false};
    std::size_t weak_streak_{0}, active_{0};
};

}  // namespace touch
