#include <cstdio>

int main() {
    int n = 1;
    auto byValue = [n]  { return n; };   // поле-копія: 1
    auto byRef   = [&n] { return n; };   // поле-посилання на n

    n = 42;

    std::printf("%d %d\n", byValue(), byRef());   // 1 42
}
