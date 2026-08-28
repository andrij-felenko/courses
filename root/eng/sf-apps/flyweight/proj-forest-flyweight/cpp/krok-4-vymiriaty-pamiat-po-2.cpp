#include <random>

int main() {
    long before = resident_kib();

    TreeKindFactory kinds;
    const TreeKind* species[] = {
        kinds.get("oak"), kinds.get("pine"), kinds.get("birch"),
    };

    Forest forest;
    forest.reserve(1'000'000);                       // точний буфер, без запасу
    std::mt19937 rng(42);
    std::uniform_real_distribution<float> pos(0.f, 10000.f), sc(0.7f, 1.4f);
    for (int i = 0; i < 1'000'000; ++i)
        forest.plant(pos(rng), 0.f, pos(rng), sc(rng), species[i % 3]);

    long after = resident_kib();
    std::printf("дерев: %zu   приріст RSS: %.1f МБ\n",
                forest.size(), (after - before) / 1024.0);
}
