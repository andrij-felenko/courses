#include <boost/function.hpp>
#include <boost/bind.hpp>
#include <iostream>

struct Calculator {
    void add(int a, int b) { std::cout << (a + b) << '\n'; }
};

void legacy_print(int result) {
    std::cout << "Result: " << result << '\n';
}

int main() {
    // Boost.Function зберігає як вказівники на функції, так і зв'язані методи
    boost::function<void(int, int)> func1 = &legacy_print; // Адаптація сигнатури
    
    Calculator calc;
    boost::function<void()> func2 = boost::bind(&Calculator::add, &calc, 10, 20);
    
    func2(); // Друкує 30
}
