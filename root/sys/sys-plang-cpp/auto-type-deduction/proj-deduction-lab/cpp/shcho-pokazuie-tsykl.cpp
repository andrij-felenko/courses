int main() {
    std::vector<Probe> v;
    v.reserve(1000);
    for (int i = 0; i < 1000; ++i)
        v.emplace_back("елемент-номер-" + std::to_string(i) + "-із-довгим-хвостом");

    measure("for (auto x : v)       ", [&] {
        for (auto x : v)        g_sink += x.id.size();
    });
    measure("for (const auto& x : v)", [&] {
        for (const auto& x : v) g_sink += x.id.size();
    });
    measure("for (auto&& x : v)     ", [&] {
        for (auto&& x : v)      g_sink += x.id.size();
    });
}
