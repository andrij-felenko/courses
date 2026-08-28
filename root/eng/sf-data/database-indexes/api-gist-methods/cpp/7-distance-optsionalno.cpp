#include <iostream>
#include <span>
#include <vector>
#include <algorithm>
#include <cmath>

/* Двовимірний обмежувальний прямокутник (Bounding Box) */
struct BoundingBox {
    double xmin{0.0}, ymin{0.0}, xmax{0.0}, ymax{0.0};

    [[nodiscard]] double area() const noexcept {
        return std::max(0.0, xmax - xmin) * std::max(0.0, ymax - ymin);
    }

    [[nodiscard]] bool intersects(const BoundingBox& other) const noexcept {
        return !(xmin > other.xmax || xmax < other.xmin ||
                 ymin > other.ymax || ymax < other.ymin);
    }

    [[nodiscard]] BoundingBox enclose(const BoundingBox& other) const noexcept {
        return {
            std::min(xmin, other.xmin),
            std::min(ymin, other.ymin),
            std::max(xmax, other.xmax),
            std::max(ymax, other.ymax)
        };
    }
};

/* C++ реалізація логіки обчислення штрафу та перевірки предикатів */
class BoxGistOperator final {
public:
    [[nodiscard]] static bool consistent(const BoundingBox& entry_box,
                                         const BoundingBox& query_box,
                                         uint16_t strategy,
                                         bool& out_recheck) noexcept {
        out_recheck = false;
        switch (strategy) {
            case 1: /* Перетин (Overlaps: &&) */
                return entry_box.intersects(query_box);
            case 2: /* Вміщення (Contains: @>) */
                return entry_box.xmin <= query_box.xmin && entry_box.xmax >= query_box.xmax &&
                       entry_box.ymin <= query_box.ymin && entry_box.ymax >= query_box.ymax;
            default:
                return false;
        }
    }

    [[nodiscard]] static BoundingBox compute_union(std::span<const BoundingBox> boxes) noexcept {
        if (boxes.empty()) return {};
        BoundingBox acc = boxes.front();
        for (size_t i = 1; i < boxes.size(); ++i) {
            acc = acc.enclose(boxes[i]);
        }
        return acc;
    }

    [[nodiscard]] static float penalty(const BoundingBox& orig_box,
                                       const BoundingBox& new_box) noexcept {
        const double current_area = orig_box.area();
        const double union_area = orig_box.enclose(new_box).area();
        return static_cast<float>(union_area - current_area);
    }
};
