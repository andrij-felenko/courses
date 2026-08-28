#include <print>
#include <string_view>

int main() {
    std::string_view user = "Олексій";
    int score = 2500;

    // C++23 std::print: прямоточний вивід без створення std::string
    std::print("Вітаємо, {}! Ваш результат: {} балів.\n", user, score);

    // std::println автоматично додає символ нового рядка '\n' у кінці
    std::println("Гра завершена успішно.");
}
