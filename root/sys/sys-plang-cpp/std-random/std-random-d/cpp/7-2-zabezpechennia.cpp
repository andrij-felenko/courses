#include <iostream>
#include <random>
#include <cassert>

void verify_reproducibility() {
    std::mt19937 rng1(1337);
    std::mt19937 rng2(1337);

    std::uniform_real_distribution<double> dist(0.0, 1.0);

    for (int i = 0; i < 1000; ++i) {
        // Обидві послідовності збігаються біт-в-біт
        assert(dist(rng1) == dist(rng2));
    }
    std::cout << "✔ Відтворюваність повністю підтверджена!\n";
}
