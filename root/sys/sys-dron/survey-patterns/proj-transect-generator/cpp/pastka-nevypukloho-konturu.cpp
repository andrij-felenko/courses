    const Polygon bay{ {0.0, 0.0}, {200.0, 0.0}, {200.0, 120.0}, {120.0, 120.0},
                       {120.0, 30.0}, {80.0, 30.0}, {80.0, 120.0}, {0.0, 120.0} };

    for (int pass = 0; pass < 2; ++pass) {
        const bool pairRule = (pass == 1);
        const std::vector<Transect> t = buildTransects(bay, 0.0, step, 0.0,  Entry::BottomLeft, pairRule);
        const std::vector<Transect> r = buildTransects(bay, 0.0, step, turn, Entry::BottomLeft, pairRule);

        double len = 0.0;
        for (const Transect &s : t) len += std::hypot(s.b.x - s.a.x, s.b.y - s.a.y);

        std::printf("%s: галсів %zu, покриття %.2f м, маршрут %.2f м\n",
                    pairRule ? "пари по черзі" : "дві найдальші", t.size(), len, routeLength(r));
    }
