#include <iostream>
#include <string>
#include <string_view>

std::string_view make_greeting(const std::string& name) {
    std::string text = "Вітаємо, " + name + "!";
    return text; // Компілятор попереджає, але код успішно транслюється
}

int main() {
    std::string_view greeting = make_greeting("Марія");
    std::cout << greeting << '\n'; // ← що саме з'явиться в терміналі?
}
