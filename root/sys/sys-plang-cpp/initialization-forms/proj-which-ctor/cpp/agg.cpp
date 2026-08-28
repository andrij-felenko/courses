// agg.cpp — g++ -std=c++17 agg.cpp && g++ -std=c++20 agg.cpp
#include <cstdio>
#include <type_traits>

struct Rect { int w; int h = 10; };        // агрегат
struct Tag  { Tag() = default; int v; };   // агрегат у C++17, НЕ агрегат у C++20

int main() {
    std::printf("__cplusplus = %ld\n", (long)__cplusplus);

#ifdef __cpp_aggregate_paren_init
    std::printf("__cpp_aggregate_paren_init = %ld\n", (long)__cpp_aggregate_paren_init);
    Rect a(3, 4);
    Rect b(3);
    Rect c(3.9, 4);                        // звуження круглими ДОЗВОЛЕНЕ
    std::printf("Rect a(3, 4)   → %d × %d\n", a.w, a.h);
    std::printf("Rect b(3)      → %d × %d\n", b.w, b.h);
    std::printf("Rect c(3.9, 4) → %d × %d\n", c.w, c.h);
#else
    std::puts("круглі дужки для агрегату недоступні");
#endif

    Rect d{3, 4};
    std::printf("Rect d{3, 4}   → %d × %d\n", d.w, d.h);

#if __cplusplus < 202002L
    Tag t{7};
    std::printf("Tag t{7}       → v = %d  (Tag ще агрегат)\n", t.v);
#else
    std::puts("Tag t{7}       → не компілюється: Tag більше не агрегат");
#endif

    std::printf("is_constructible<Rect, int, int> = %d\n",
                (int)std::is_constructible<Rect, int, int>::value);
}
