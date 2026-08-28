#include <format>
#include <string>
#include <iostream>

int main() {
    std::string name = "Олександр";
    int count = 5;

    // Автоматична нумерація аргументів (по порядку передачі)
    std::string s1 = std::format("{} придбав {} товарів", name, count);

    // Явна позиційна нумерація (ідеально для локалізації та перекладів)
    // Німецький варіант вимоги іншого порядку слів: "5 товарів було куплено Олександром"
    std::string s2 = std::format("{1} items bought by {0}", name, count);

    std::cout << s1 << "\n" << s2 << "\n";
}
