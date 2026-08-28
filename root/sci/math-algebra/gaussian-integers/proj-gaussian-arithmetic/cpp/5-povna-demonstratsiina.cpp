int main() {
    std::cout << "=== Демонстрація арифметики ℤ[i] (C++20) ===\n\n";

    // 1. Алгоритм Евкліда
    const GaussianInteger a{11, 3};
    const GaussianInteger b{1, 8};
    const auto g = to_primary_associate(gcd(a, b));
    std::cout << "1. НСД для чисел (" << a << ") та (" << b << "):\n";
    std::cout << "   gcd = " << g << ", норма = " << g.norm() << "\n\n";

    // 2. Алгоритм Корначчі для розкладу p = a^2 + b^2
    const uint64_t p = 2029;
    std::cout << "2. Пошук розкладу p = " << p << " на суму квадратів:\n";
    if (auto res = find_sum_of_two_squares(p)) {
        auto [sq_a, sq_b] = *res;
        std::cout << "   " << p << " = " << sq_a << "^2 + " << sq_b << "^2 = "
                  << sq_a * sq_a << " + " << sq_b * sq_b << "\n\n";
    } else {
        std::cout << "   Розклад неможливий (p != 1 mod 4)\n\n";
    }

    // 3. Повна факторизація гауссового числа
    const GaussianInteger num{30, 10};
    const auto fact = factorize(num);
    std::cout << "3. Факторизація числа (" << num << "), норма = " << num.norm() << ":\n";
    std::cout << "   Одиниця розкладу: " << fact.unit << "\n";
    for (size_t i = 0; i < fact.factors.size(); ++i) {
        const auto& [prime, power] = fact.factors[i];
        std::cout << "   Множник " << i + 1 << ": (" << prime << ")^" << power
                  << " (норма " << prime.norm() << ")\n";
    }

    return 0;
}
