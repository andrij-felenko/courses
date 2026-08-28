#include <cmath>
#include <cstddef>
#include <vector>

struct Pt { double x, y; };

// подвоєна орієнтована площа трикутника oab; її модуль, поділений на |ab|,
// дорівнює відстані точки b від прямої oa
static double cross(Pt o, Pt a, Pt b) {
    return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
}

// hull — вершини опуклої оболонки проти годинникової стрілки, без повторів і
// без трьох точок на одній прямій. Повертає найменшу ширину; у *bestEdge —
// індекс сторони, на яку лягла опорна пряма.
double minWidth(const std::vector<Pt>& hull, std::size_t* bestEdge) {
    const std::size_t n = hull.size();
    if (n < 3) return 0.0;

    std::size_t apex = 1;                 // вершина навпроти сторони 0
    double best = HUGE_VAL;
    for (std::size_t k = 0; k < n; ++k) {
        const Pt a = hull[k];
        const Pt b = hull[(k + 1) % n];
        // губка пішла за стороною k; апекс іде лише вперед, поки відстань росте
        while (std::fabs(cross(a, b, hull[(apex + 1) % n])) >
               std::fabs(cross(a, b, hull[apex])))
            apex = (apex + 1) % n;

        const double len = std::hypot(b.x - a.x, b.y - a.y);
        const double w   = std::fabs(cross(a, b, hull[apex])) / len;
        if (w < best) { best = w; if (bestEdge) *bestEdge = k; }
    }
    return best;
}
