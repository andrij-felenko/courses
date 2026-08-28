#include <cstddef>
#include <cstring>
#include <iostream>
#include <type_traits>
#include <utility>
#include <vector>

struct Stats {
    long ctor = 0, dtor = 0;
    long copy_ctor = 0, copy_assign = 0;
    long move_ctor = 0, move_assign = 0;
    long long bytes_copied = 0;
};

inline Stats g;                       // inline-змінна: одна на всю програму (C++17)

void report(const char* what, const Stats& before) {
    std::cout << what << " |";
    auto item = [](const char* name, long long delta) {
        if (delta) std::cout << "  " << name << ' ' << delta;
    };
    item("ctor",      g.ctor        - before.ctor);
    item("copy-ctor", g.copy_ctor   - before.copy_ctor);
    item("move-ctor", g.move_ctor   - before.move_ctor);
    item("copy-asg",  g.copy_assign - before.copy_assign);
    item("move-asg",  g.move_assign - before.move_assign);
    item("dtor",      g.dtor        - before.dtor);
    item("MiB",      (g.bytes_copied - before.bytes_copied) >> 20);
    std::cout << '\n';
}
