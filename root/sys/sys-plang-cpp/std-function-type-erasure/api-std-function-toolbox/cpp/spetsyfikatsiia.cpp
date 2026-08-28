#include <functional>
#include <memory>
#include <iostream>

int main() {
    auto ptr = std::make_unique<int>(100);

    // 1. Move-Only лямбда із кваліфікатором const
    std::move_only_function<int() const> fn1 = [p = std::move(ptr)]() {
        return *p;
    };
    std::cout << fn1() << '\n';

    // 2. One-Shot лямбда (можна викликати лише один раз через rvalue)
    auto resource = std::make_unique<std::string>("Data Buffer");
    std::move_only_function<void() &&> fn_once = [r = std::move(resource)]() mutable {
        std::cout << "Processing " << *r << '\n';
        r.reset();
    };

    // fn_once(); // ПОМИЛКА КОМПІЛЯЦІЇ: fn_once має кваліфікатор &&
    std::move(fn_once)(); // Успішно!
}
