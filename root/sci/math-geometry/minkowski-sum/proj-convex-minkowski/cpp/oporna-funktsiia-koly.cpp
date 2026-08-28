#include <cstdio>

// Найдальша точка багатокутника в напрямі u. Строге «>» — щоб за рівності
// відповідь була та сама, інакше GJK зациклиться на перпендикулярному ребрі.
Pt far(const std::vector<Pt>& v, Pt u) {
    size_t best = 0;
    long long bestDot = v[0].x * u.x + v[0].y * u.y;
    for (size_t i = 1; i < v.size(); ++i) {
        const long long d = v[i].x * u.x + v[i].y * u.y;
        if (d > bestDot) { bestDot = d; best = i; }
    }
    return v[best];
}

// Опорна точка множини різниць A ⊕ (−B) — без побудови самої множини.
Pt support(const std::vector<Pt>& A, const std::vector<Pt>& B, Pt u) {
    return far(A, u) - far(B, -u);
}

int main() {
    const std::vector<Pt> tri = {{0, 0}, {4, 0}, {0, 3}};
    const std::vector<Pt> sq  = {{0, 0}, {1, 0}, {1, 1}, {0, 1}};

    for (Pt p : minkowski(tri, sq)) printf("(%lld,%lld) ", p.x, p.y);
    putchar('\n');

    std::vector<Pt> away;                       // той самий трикутник, зсунутий убік
    for (Pt p : tri) away.push_back(p + Pt{10, 0});
    printf("%d %d\n", convexIntersect(tri, sq), convexIntersect(tri, away));
}
