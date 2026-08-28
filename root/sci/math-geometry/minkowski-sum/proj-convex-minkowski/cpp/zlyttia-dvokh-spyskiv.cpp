// Сума Мінковського двох опуклих багатокутників — O(m + n).
std::vector<Pt> minkowski(std::vector<Pt> a, std::vector<Pt> b) {
    normalize(a);
    normalize(b);
    const size_t n = a.size(), m = b.size();

    const Pt a0 = a[0], a1 = a[1 % n], b0 = b[0], b1 = b[1 % m];
    a.push_back(a0); a.push_back(a1);      // хвіст, щоб не брати індекси за модулем
    b.push_back(b0); b.push_back(b1);

    std::vector<Pt> res;
    res.reserve(n + m);
    size_t i = 0, j = 0;
    while (i < n || j < m) {
        res.push_back(a[i] + b[j]);
        const long long c = cross(a[i + 1] - a[i], b[j + 1] - b[j]);
        if (c >= 0 && i < n) ++i;          // ребро A за напрямом не пізніше — беремо його
        if (c <= 0 && j < m) ++j;          // ребро B за напрямом не пізніше — беремо його
    }
    return res;
}
