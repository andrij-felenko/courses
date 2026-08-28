#include <iostream>
#include <vector>
#include <string>
#include <span>
#include <expected>
#include <cstdint>

int main() {
    std::cout << "=== Демонстрація використання C++ API Арифметичної Ієрархії ===\n\n";

    const std::vector<QuantifierDescriptor> total_prefix{
        { QuantifierKind::Forall, "x", false, 0 },
        { QuantifierKind::Exists, "s", false, 0 }
    };

    const auto result = classify_prefix(total_prefix);

    if (result) {
        std::cout << "Успішна класифікація формули:\n";
        std::cout << " - Початкових кванторів:  " << result->raw_quantifier_count << "\n";
        std::cout << " - Згорнутих кванторів:   " << result->contracted_count << "\n";
        std::cout << " - Рівень ієрархії (n):   " << result->level_n << "\n";
        std::cout << " - Потрібний оракул:      0^(" << result->oracle_jump_required << ")\n";
    } else {
        std::cerr << "Помилка класифікації: " << result.error() << "\n";
    }

    const auto paired = cantor_encode(42, 100);
    if (paired) {
        std::cout << "\nПарування Кантора: <42, 100> = " << *paired << "\n";
    }

    return 0;
}
