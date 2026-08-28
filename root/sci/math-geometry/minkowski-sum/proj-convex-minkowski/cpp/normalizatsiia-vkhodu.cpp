#include <algorithm>
#include <vector>

struct Pt {
    long long x, y;
    Pt operator+(Pt o) const { return {x + o.x, y + o.y}; }
    Pt operator-(Pt o) const { return {x - o.x, y - o.y}; }
    Pt operator-()     const { return {-x, -y}; }
    bool operator==(Pt o) const { return x == o.x && y == o.y; }
};

// z-складова векторного добутку: >0 — b лівіше a, <0 — правіше, 0 — той самий напрям
inline long long cross(Pt a, Pt b) { return a.x * b.y - a.y * b.x; }

// Без повторів і вершин посеред ребра, обхід проти годинникової стрілки,
// вершина 0 — найнижча, а серед рівних — найлівіша.
void normalize(std::vector<Pt>& p) {
    if (p.empty()) return;
    p.erase(std::unique(p.begin(), p.end()), p.end());
    while (p.size() > 1 && p.front() == p.back()) p.pop_back();

    long long area2 = 0;                        // подвоєна орієнтована площа
    for (size_t i = 0, n = p.size(); i < n; ++i) area2 += cross(p[i], p[(i + 1) % n]);
    if (area2 < 0) std::reverse(p.begin(), p.end());   // ==0 — точка або відрізок, лишаємо

    if (p.size() > 2) {                         // викинути вершини всередині ребра
        std::vector<Pt> r;
        r.reserve(p.size());
        for (Pt v : p) {
            while (r.size() >= 2 && cross(r.back() - r[r.size() - 2], v - r.back()) == 0)
                r.pop_back();
            r.push_back(v);
        }
        while (r.size() > 2 && cross(r.back() - r[r.size() - 2], r[0] - r.back()) == 0)
            r.pop_back();
        while (r.size() > 2 && cross(r[0] - r.back(), r[1] - r[0]) == 0)
            r.erase(r.begin());
        p.swap(r);
    }

    size_t k = 0;
    for (size_t i = 1; i < p.size(); ++i)
        if (p[i].y < p[k].y || (p[i].y == p[k].y && p[i].x < p[k].x)) k = i;
    std::rotate(p.begin(), p.begin() + k, p.end());
}
