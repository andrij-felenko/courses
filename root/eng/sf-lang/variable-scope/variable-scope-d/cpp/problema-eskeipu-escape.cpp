#include <iostream>
#include <functional>
#include <memory>

// Небезпечний випадок: повернення лямбди із захопленням за посиланням [&]
std::function<int()> create_broken_counter() {
    int local_val = 42;
    // Катастрофа: local_val знищується на стеку при виході з функції!
    // Лямбда зберігає посилання на мертву пам'ять (Dangling Reference).
    return [&]() { return ++local_val; }; 
}

// Коректний випадок: захоплення за значенням [=] або переміщення [val = std::move(...)]
std::function<int()> create_safe_counter() {
    int local_val = 42;
    // local_val безпечно копіюється всередину об'єкта-замикання
    return [local_val]() mutable { return ++local_val; }; 
}

int main() {
    auto safe_fn = create_safe_counter();
    std::cout << "Safe call 1: " << safe_fn() << '\n'; // 43
    std::cout << "Safe call 2: " << safe_fn() << '\n'; // 44
    return 0;
}
