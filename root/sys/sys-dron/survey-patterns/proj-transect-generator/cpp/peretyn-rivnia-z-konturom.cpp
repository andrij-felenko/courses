// Усі x, у яких контур перетинає горизонталь y = yLine, за зростанням.
std::vector<double> crossings(const Polygon &poly, double yLine) {
    std::vector<double> xs;
    const size_t n = poly.size();
    for (size_t i = 0; i < n; ++i) {
        const Vec2 &p = poly[i];
        const Vec2 &q = poly[(i + 1) % n];
        if ((p.y > yLine) == (q.y > yLine)) continue;   // сторона не переходить рівень
        const double t = (yLine - p.y) / (q.y - p.y);   // знаменник тут не нуль
        xs.push_back(p.x + t * (q.x - p.x));
    }
    std::sort(xs.begin(), xs.end());
    return xs;
}
