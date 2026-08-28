#include <stdbool.h>

typedef struct { float x; float y; } pt_t;   // координати на площині

// Метод променя: чи точка p всередині багатокутника з n вершин verts[].
// Промінь пускаємо горизонтально праворуч; inside перемикається на кожному
// перетині сторони — фінальний стан і є відповідь (парність числа перетинів).
bool point_in_polygon(pt_t p, const pt_t *verts, int n) {
    bool inside = false;
    for (int i = 0, j = n - 1; i < n; j = i++) {
        // Умова 1: сторона (verts[j] → verts[i]) накриває рівень p.y по вертикалі.
        bool straddles = (verts[i].y > p.y) != (verts[j].y > p.y);
        if (straddles) {
            // Умова 2: точка перетину сторони з горизонталлю лежить правіше p.x.
            float x_cross = verts[i].x
                + (p.y - verts[i].y) * (verts[j].x - verts[i].x)
                                     / (verts[j].y - verts[i].y);
            if (p.x < x_cross)
                inside = !inside;      // перетин — перемкнути парність
        }
    }
    return inside;
}
