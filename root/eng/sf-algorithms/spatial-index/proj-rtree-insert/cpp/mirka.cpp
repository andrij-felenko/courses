#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>

struct Rect { double x1, y1, x2, y2; };        // x1 ≤ x2, y1 ≤ y2

static double area(const Rect& r) { return (r.x2 - r.x1) * (r.y2 - r.y1); }

static Rect unite(const Rect& a, const Rect& b) {           // спільний MBR
    return Rect{ std::min(a.x1, b.x1), std::min(a.y1, b.y1),
                 std::max(a.x2, b.x2), std::max(a.y2, b.y2) };
}

static double enlargement(const Rect& box, const Rect& add) {
    return area(unite(box, add)) - area(box);               // ціна впустити add
}

static bool intersects(const Rect& a, const Rect& b) {
    return !(a.x2 < b.x1 || b.x2 < a.x1 || a.y2 < b.y1 || b.y2 < a.y1);
}
