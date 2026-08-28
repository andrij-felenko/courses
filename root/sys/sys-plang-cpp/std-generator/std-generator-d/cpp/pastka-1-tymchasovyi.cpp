#include <generator>
#include <string>
#include <iostream>

// НЕБЕЗПЕЧНО: передача const std::string&
std::generator<char> print_letters(const std::string& text) {
    for (char c : text) {
        co_yield c;
    }
}

std::generator<char> make_dangling_generator() {
    // ПОМИЛКА: Створення тимчасового рядка!
    // Тимчасовий рядок знищується наприкінці цього рядка.
    // Кадр корутини зберігає посилання на вже знищену пам'ять!
    return print_letters(std::string("Hello World")); 
}

int main() {
    auto gen = make_dangling_generator();
    // Виклик begin() звертається до мертва пам'яті -> UNDEFINED BEHAVIOR!
    for (char c : gen) {
        std::cout << c;
    }
}
