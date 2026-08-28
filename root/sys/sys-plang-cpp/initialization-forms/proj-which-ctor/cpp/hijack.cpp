// hijack.cpp
// g++ -std=c++17 hijack.cpp -o h1
// g++ -std=c++17 -DWITH_LIST_CTOR hijack.cpp -o h2
#include <cstdio>
#include <initializer_list>

struct Grid {
    Grid(int r, int c) {
        std::printf("  Grid(int, int)               сітка %d × %d = %d клітинок\n",
                    r, c, r * c);
    }
#ifdef WITH_LIST_CTOR
    Grid(std::initializer_list<int> cells) {
        std::printf("  Grid(initializer_list<int>)  список (%u):", (unsigned)cells.size());
        for (int v : cells) std::printf(" %d", v);
        std::putchar('\n');
    }
#endif
};

int main() {
    std::puts("Grid a{3, 4};");  Grid a{3, 4};
    std::puts("Grid b(3, 4);");  Grid b(3, 4);
}
