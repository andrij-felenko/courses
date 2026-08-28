#include <iostream>
#include <string_view>
#include <string>

std::string_view format_greeting(const std::string& name) {
    std::string message = "Привіт, " + name + "!";
    return std::string_view(message); // Повертає view на тимчасовий локальний об'єкт
}

void overwrite_stack() {
    volatile double array[32];
    for (int i = 0; i < 32; ++i) array[i] = 3.14159;
}

int main() {
    std::string_view greeting = format_greeting("Олексій");
    
    overwrite_stack(); // Перезаписує пам'ять старого кадру
    
    // Помилка: читання мертвого стека через string_view
    std::cout << greeting << '\n';
    return 0;
}
