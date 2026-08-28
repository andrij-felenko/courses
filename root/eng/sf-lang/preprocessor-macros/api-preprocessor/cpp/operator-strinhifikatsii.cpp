#include <iostream>
#include <string_view>

#define STRINGIFY_VAL(x) #x

int main() {
    constexpr std::string_view expr = STRINGIFY_VAL(a + b * (c - d));
    std::cout << "Результат: " << expr << "\n";
    return 0;
}
