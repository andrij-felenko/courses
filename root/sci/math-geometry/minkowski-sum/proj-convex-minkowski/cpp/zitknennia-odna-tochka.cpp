// Чи лежить q в опуклому CCW-багатокутнику v (межа рахується всередині). O(log n).
// v уже нормалізований, тож v[0] — опорна вершина віяла.
bool pointInConvex(const std::vector<Pt>& v, Pt q) {
    const size_t n = v.size();
    if (n == 1) return q == v[0];
    if (n == 2) {                                   // вироджений випадок — відрізок
        const Pt d = v[1] - v[0], e = q - v[0];
        const long long t = d.x * e.x + d.y * e.y;
        return cross(d, e) == 0 && t >= 0 && t <= d.x * d.x + d.y * d.y;
    }
    if (cross(v[1] - v[0], q - v[0]) < 0) return false;       // поза віялом з одного боку
    if (cross(v[n - 1] - v[0], q - v[0]) > 0) return false;   // ...і з другого

    size_t lo = 1, hi = n - 1;                      // шукаємо сектор між lo та lo+1
    while (hi - lo > 1) {
        const size_t mid = (lo + hi) / 2;
        if (cross(v[mid] - v[0], q - v[0]) >= 0) lo = mid; else hi = mid;
    }
    return cross(v[hi] - v[lo], q - v[lo]) >= 0;    // з внутрішнього боку ребра
}

// Чи перетинаються два опуклі багатокутники.
bool convexIntersect(const std::vector<Pt>& A, const std::vector<Pt>& B) {
    std::vector<Pt> mirrored;
    mirrored.reserve(B.size());
    for (Pt p : B) mirrored.push_back(-p);          // саме −B, а не зсув B
    return pointInConvex(minkowski(A, mirrored), Pt{0, 0});
}
