    std::map<int, Probe> m;
    for (int i = 0; i < 1000; ++i)
        m.emplace(i, Probe("ключ-" + std::to_string(i) + "-із-довгим-хвостом"));

    measure("const std::pair<int, Probe>& e", [&] {
        for (const std::pair<int, Probe>& e : m) g_sink += e.second.id.size();
    });
    measure("const auto& e                 ", [&] {
        for (const auto& e : m)                  g_sink += e.second.id.size();
    });
