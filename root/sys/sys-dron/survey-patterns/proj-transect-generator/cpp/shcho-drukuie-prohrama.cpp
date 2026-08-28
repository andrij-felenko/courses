int main() {
    const Polygon field{ {0.0, 0.0}, {50.0, 240.0}, {225.0, 275.0}, {275.0, 50.0}, {145.0, -50.0} };
    const double angle = 30.0, step = 26.44, turn = 30.0;

    const std::vector<Transect> bare = buildTransects(field, angle, step, 0.0,  Entry::BottomLeft, false);
    const std::vector<Transect> full = buildTransects(field, angle, step, turn, Entry::BottomLeft, false);

    double covered = 0.0;
    for (const Transect &s : bare) covered += std::hypot(s.b.x - s.a.x, s.b.y - s.a.y);

    std::printf("поле %zu вершин, кут %.1f, крок %.2f м, розворот %.1f м\n",
                field.size(), angle, step, turn);
    std::printf("галсів %zu, покриття %.2f м, маршрут %.2f м\n\n",
                bare.size(), covered, routeLength(full));

    for (size_t i = 0; i < bare.size(); ++i)
        std::printf("  %2zu  %7.2f м   (%8.2f,%8.2f) -> (%8.2f,%8.2f)\n", i,
                    std::hypot(bare[i].b.x - bare[i].a.x, bare[i].b.y - bare[i].a.y),
                    bare[i].a.x, bare[i].a.y, bare[i].b.x, bare[i].b.y);

    const char *corner[] = { "лівий нижній", "правий нижній", "лівий верхній", "правий верхній" };
    for (int e = 0; e < 4; ++e) {
        const std::vector<Transect> v =
            buildTransects(field, angle, step, turn, static_cast<Entry>(e), false);
        std::printf("\nвхід %s: (%.2f, %.2f)", corner[e], v.front().a.x, v.front().a.y);
    }
    std::printf("\n");
    return 0;
}
