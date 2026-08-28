#include <functional>
#include <iostream>
#include <string>

std::function<void()> create_task() {
    std::string secret = "X99-PRO-AUTH";
    
    // Небезпека: лямбда захоплює secret за посиланням на локальний стек
    return [&secret]() {
        std::cout << "Авторизація: " << secret << '\n';
    };
}

int main() {
    auto task = create_task();
    // Локальна змінна secret знищена!
    task(); // Use-After-Free: читання мертвого стека
}
