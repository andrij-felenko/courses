#include <iostream>
#include <vector>
#include <set>
#include <queue>
#include <optional>
#include <cmath>
#include <algorithm>

namespace geom {

struct Point {
    double x{0.0};
    double y{0.0};

    bool operator==(const Point& other) const {
        return std::abs(x - other.x) < 1e-9 && std::abs(y - other.y) < 1e-9;
    }
};

struct Segment {
    int id{0};
    Point p1{}; // Лівий кінець (p1.x <= p2.x)
    Point p2{}; // Правий кінець

    Segment(int id_, Point a, Point b) : id(id_) {
        if (a.x < b.x || (std::abs(a.x - b.x) < 1e-9 && a.y < b.y)) {
            p1 = a; p2 = b;
        } else {
            p1 = b; p2 = a;
        }
    }

    [[nodiscard]] double y_at(double current_x) const noexcept {
        if (std::abs(p2.x - p1.x) < 1e-9) return p1.y;
        const double t = (current_x - p1.x) / (p2.x - p1.x);
        return p1.y + t * (p2.y - p1.y);
    }
};

// Предикат орієнтації поворотів (векторний косий добуток)
inline double cross_product(Point a, Point b, Point c) noexcept {
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

inline bool on_segment(Point p, Point q, Point r) noexcept {
    return q.x <= std::max(p.x, r.x) && q.x >= std::min(p.x, r.x) &&
           q.y <= std::max(p.y, r.y) && q.y >= std::min(p.y, r.y);
}

// Знаходження перетину двох відрізків
std::optional<Point> find_intersection(const Segment& s1, const Segment& s2) {
    const Point a = s1.p1, b = s1.p2;
    const Point c = s2.p1, d = s2.p2;

    const double d1 = cross_product(a, b, c);
    const double d2 = cross_product(a, b, d);
    const double d3 = cross_product(c, d, a);
    const double d4 = cross_product(c, d, b);

    if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
        ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) {
        const double a1 = b.y - a.y;
        const double b1 = a.x - b.x;
        const double c1 = a1 * a.x + b1 * a.y;

        const double a2 = d.y - c.y;
        const double b2 = c.x - d.x;
        const double c2 = a2 * c.x + b2 * c.y;

        const double det = a1 * b2 - a2 * b1;
        if (std::abs(det) > 1e-9) {
            return Point{(b2 * c1 - b1 * c2) / det, (a1 * c2 - a2 * c1) / det};
        }
    }

    if (std::abs(d1) < 1e-9 && on_segment(a, c, b)) return c;
    if (std::abs(d2) < 1e-9 && on_segment(a, d, b)) return d;
    if (std::abs(d3) < 1e-9 && on_segment(c, a, d)) return a;
    if (std::abs(d4) < 1e-9 && on_segment(c, b, d)) return b;

    return std::nullopt;
}

enum class EventType { End, Intersect, Start };

struct Event {
    double x{0.0};
    double y{0.0};
    EventType type{EventType::Start};
    int seg1_id{-1};
    int seg2_id{-1};

    bool operator>(const Event& other) const noexcept {
        if (std::abs(x - other.x) > 1e-9) return x > other.x;
        if (type != other.type) return type > other.type;
        return y > other.y;
    }
};

// Компаратор для червоно-чорного дерева статусу (std::set)
struct StatusComparator {
    const std::vector<Segment>& segs;
    double sweep_x{0.0};

    bool operator()(int id1, int id2) const {
        if (id1 == id2) return false;
        const double y1 = segs[id1].y_at(sweep_x);
        const double y2 = segs[id2].y_at(sweep_x);
        if (std::abs(y1 - y2) > 1e-9) {
            return y1 < y2;
        }
        // Якщо висоти збігаються, порівнюємо кутові коефіцієнти праворуч
        return id1 < id2;
    }
};

class SweepLineSolver {
public:
    explicit SweepLineSolver(std::vector<Segment> segments)
        : segments_(std::move(segments)) {}

    [[nodiscard]] std::vector<std::pair<int, int>> compute_intersections() {
        std::priority_queue<Event, std::vector<Event>, std::greater<>> event_queue;
        std::vector<std::pair<int, int>> result;

        // Ініціалізація черги початковими подіями
        for (const auto& seg : segments_) {
            event_queue.push(Event{seg.p1.x, seg.p1.y, EventType::Start, seg.id, -1});
            event_queue.push(Event{seg.p2.x, seg.p2.y, EventType::End, seg.id, -1});
        }

        StatusComparator comp{segments_, 0.0};
        std::set<int, StatusComparator> status_tree(comp);

        auto check_and_add_intersection = [&](int id1, int id2, double current_x) {
            if (id1 < 0 || id2 < 0) return;
            const auto pt = find_intersection(segments_[id1], segments_[id2]);
            if (pt && pt->x > current_x - 1e-9) {
                event_queue.push(Event{pt->x, pt->y, EventType::Intersect, id1, id2});
            }
        };

        while (!event_queue.empty()) {
            const Event ev = event_queue.top();
            event_queue.pop();

            // Оновлюємо положення замітальної прямої в компараторі
            comp.sweep_x = ev.x;

            if (ev.type == EventType::Start) {
                auto it = status_tree.insert(ev.seg1_id).first;
                auto prev = (it != status_tree.begin()) ? std::prev(it) : status_tree.end();
                auto next = std::next(it);

                if (prev != status_tree.end()) check_and_add_intersection(*prev, ev.seg1_id, ev.x);
                if (next != status_tree.end()) check_and_add_intersection(ev.seg1_id, *next, ev.x);
            } else if (ev.type == EventType::End) {
                auto it = status_tree.find(ev.seg1_id);
                if (it != status_tree.end()) {
                    auto prev = (it != status_tree.begin()) ? std::prev(it) : status_tree.end();
                    auto next = std::next(it);
                    if (prev != status_tree.end() && next != status_tree.end()) {
                        check_and_add_intersection(*prev, *next, ev.x);
                    }
                    status_tree.erase(it);
                }
            } else if (ev.type == EventType::Intersect) {
                result.emplace_back(std::min(ev.seg1_id, ev.seg2_id), std::max(ev.seg1_id, ev.seg2_id));
            }
        }

        std::sort(result.begin(), result.end());
        result.erase(std::unique(result.begin(), result.end()), result.end());
        return result;
    }

private:
    std::vector<Segment> segments_;
};

} // namespace geom

int main() {
    std::vector<geom::Segment> segments{
        {0, {1.0, 1.0}, {5.0, 5.0}},
        {1, {1.0, 5.0}, {5.0, 1.0}},
        {2, {0.0, 3.0}, {6.0, 3.0}}
    };

    geom::SweepLineSolver solver(segments);
    const auto intersections = solver.compute_intersections();

    std::cout << "Знайдено перетинів: " << intersections.size() << '\n';
    for (const auto& [s1, s2] : intersections) {
        std::cout << "Перетин відрізків " << s1 << " та " << s2 << '\n';
    }
    return 0;
}
