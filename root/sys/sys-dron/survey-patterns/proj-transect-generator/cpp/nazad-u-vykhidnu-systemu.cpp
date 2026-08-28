enum class Entry { BottomLeft, BottomRight, TopLeft, TopRight };

void alignDirections(std::vector<Transect> &t) {
    if (t.empty()) return;
    const double fx = t.front().b.x - t.front().a.x;
    const double fy = t.front().b.y - t.front().a.y;
    for (Transect &s : t)
        if ((s.b.x - s.a.x) * fx + (s.b.y - s.a.y) * fy < 0.0) std::swap(s.a, s.b);
}

void setEntry(std::vector<Transect> &t, Entry e) {
    const bool flipAlong  = (e == Entry::BottomRight || e == Entry::TopRight);
    const bool flipAcross = (e == Entry::TopLeft     || e == Entry::TopRight);
    if (flipAlong)  for (Transect &s : t) std::swap(s.a, s.b);
    if (flipAcross) std::reverse(t.begin(), t.end());
}

void makeSnake(std::vector<Transect> &t) {
    for (size_t i = 1; i < t.size(); i += 2) std::swap(t[i].a, t[i].b);
}

void extendEnds(std::vector<Transect> &t, double turnaround) {
    if (!(turnaround > 0.0)) return;
    for (Transect &s : t) {
        const double dx = s.b.x - s.a.x, dy = s.b.y - s.a.y;
        const double len = std::hypot(dx, dy);
        if (!(len > 0.0)) continue;
        const double ux = dx / len * turnaround, uy = dy / len * turnaround;
        s.a = { s.a.x - ux, s.a.y - uy };
        s.b = { s.b.x + ux, s.b.y + uy };
    }
}
