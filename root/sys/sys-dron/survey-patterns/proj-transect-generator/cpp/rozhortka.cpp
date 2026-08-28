std::vector<Transect> sweep(const Polygon &rotated, const Vec2 &centre,
                            double step, bool pairRule) {
    const Box b = bounds(rotated);
    const double diagonal = std::hypot(b.xHi - b.xLo, b.yHi - b.yLo);
    if (!(diagonal > 0.0)) return {};                   // усі вершини злилися в точку

    if (!(step > diagonal / kMaxTransects))              // ловить 0, від'ємне і NaN
        step = diagonal / kMaxTransects;

    const long kLo = static_cast<long>(std::ceil ((b.yLo - centre.y) / step - 0.5));
    const long kHi = static_cast<long>(std::floor((b.yHi - centre.y) / step - 0.5));

    std::vector<Transect> out;
    for (long k = kLo; k <= kHi; ++k) {
        const double yLine = centre.y + (static_cast<double>(k) + 0.5) * step;
        const std::vector<double> xs = crossings(rotated, yLine);
        if (xs.size() < 2) continue;

        if (pairRule) {
            for (size_t i = 0; i + 1 < xs.size(); i += 2)
                if (xs[i + 1] - xs[i] > kMinLength)
                    out.push_back({ { xs[i], yLine }, { xs[i + 1], yLine } });
        } else if (xs.back() - xs.front() > kMinLength) {
            out.push_back({ { xs.front(), yLine }, { xs.back(), yLine } });
        }
    }

    if (out.empty()) {                                   // крок ширший за всю фігуру
        const std::vector<double> xs = crossings(rotated, centre.y);
        if (xs.size() >= 2 && xs.back() - xs.front() > kMinLength)
            out.push_back({ { xs.front(), centre.y }, { xs.back(), centre.y } });
    }
    return out;
}
