// vectors.cpp
#include <cstdio>
#include <string>
#include <vector>

static void show(const char* code, const std::vector<int>& v) {
    std::printf("%-28s│ розмір %u:", code, (unsigned)v.size());
    for (int x : v) std::printf(" %d", x);
    std::putchar('\n');
}
static void show(const char* code, const std::vector<std::string>& v) {
    std::printf("%-28s│ розмір %u", code, (unsigned)v.size());
    if (!v.empty()) std::printf(", [0] = \"%s\"", v[0].c_str());
    std::putchar('\n');
}

int main() {
    show("vector<int> v(3, 0)",      std::vector<int>(3, 0));
    show("vector<int> v{3, 0}",      std::vector<int>{3, 0});
    show("vector<int> v(3)",         std::vector<int>(3));
    show("vector<int> v{3}",         std::vector<int>{3});
    show("vector<int> v{}",          std::vector<int>{});
    show("vector<int> v({})",        std::vector<int>({}));
    show("vector<int> v{{}}",        std::vector<int>{{}});
    show("vector<string> v(10, \"hi\")", std::vector<std::string>(10, "hi"));
    show("vector<string> v{10, \"hi\"}", std::vector<std::string>{10, "hi"});
}
