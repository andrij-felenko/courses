#include <iostream>
#include <cassert>

void demo_client_usage_cpp() {
    // Створення ординала epsilon_0 = phi(1, 0)
    auto eps0 = veblen::make_veblen(veblen::make_finite(1), veblen::make_zero());

    // Створення ординала omega = phi(0, 1)
    auto omega = veblen::make_veblen(veblen::make_zero(), veblen::make_finite(1));

    // Обчислення суми: omega + epsilon_0 (повинно дати epsilon_0 через поглинання)
    auto sum = veblen::add(omega->clone(), eps0->clone());

    // Перевірка еквівалентності
    assert(veblen::compare(sum.get(), eps0.get()) == std::strong_ordering::equal);
}
