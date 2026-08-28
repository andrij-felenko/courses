#include <tuple>
#include <iostream>

void print_sum(int a, double b, int c) {
    std::cout << a + b + c << std::endl;
}

int main() {
    std::tuple<int, double, int> data(10, 2.5, 5);

    // Розпаковує data у виклик print_sum(10, 2.5, 5)
    std::apply(print_sum, data);
}
