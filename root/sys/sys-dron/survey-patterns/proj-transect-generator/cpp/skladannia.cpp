std::vector<Transect> buildTransects(const Polygon &field, double angleDeg, double step,
                                     double turnaround, Entry entry, bool pairRule) {
    if (field.size() < 3) return {};

    const Box  fb = bounds(field);
    const Vec2 centre{ (fb.xLo + fb.xHi) / 2.0, (fb.yLo + fb.yHi) / 2.0 };
    const double alpha = clampAngle90(angleDeg) * kDegToRad;

    Polygon rotated;
    rotated.reserve(field.size());
    for (const Vec2 &p : field) rotated.push_back(rotate(p, centre, -alpha));

    std::vector<Transect> t = sweep(rotated, centre, step, pairRule);
    for (Transect &s : t) {
        s.a = rotate(s.a, centre, alpha);
        s.b = rotate(s.b, centre, alpha);
    }

    alignDirections(t);
    setEntry(t, entry);          // порядок важить: вхід — до змійки
    makeSnake(t);
    extendEnds(t, turnaround);
    return t;
}

double routeLength(const std::vector<Transect> &t) {
    double total = 0.0;
    for (size_t i = 0; i < t.size(); ++i) {
        total += std::hypot(t[i].b.x - t[i].a.x, t[i].b.y - t[i].a.y);
        if (i > 0) total += std::hypot(t[i].a.x - t[i - 1].b.x, t[i].a.y - t[i - 1].b.y);
    }
    return total;
}
