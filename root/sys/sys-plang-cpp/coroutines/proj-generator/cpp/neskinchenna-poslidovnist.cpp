#include <cstdint>
#include <iostream>

generator<std::uint64_t> fibonacci() {
    std::uint64_t a = 0, b = 1;
    for (;;) {                       // кінця немає — і це нормально
        co_yield a;
        const std::uint64_t next = a + b;
        a = b;
        b = next;
    }
}

int main() {
    int taken = 0;
    for (std::uint64_t n : fibonacci()) {
        std::cout << n << ' ';
        if (++taken == 10) break;    // циклом володіє читач
    }
    std::cout << '\n';               // 0 1 1 2 3 5 8 13 21 34
}
