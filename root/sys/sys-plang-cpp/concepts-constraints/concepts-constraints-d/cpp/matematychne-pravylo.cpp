// Концепт 1: базове ціле число
template<typename T>
concept Integral = std::is_integral_v<T>; // Атом A

// Концепт 2: знакове ціле число
template<typename T>
concept SignedIntegral = Integral<T> && std::is_signed_v<T>; // Атоми A && B

// Кандидат 1
template<Integral T>
void advance_cursor(T step) {
    std::cout << "Загальний цілочисловий крок\n";
}

// Кандидат 2
template<SignedIntegral T>
void advance_cursor(T step) {
    std::cout << "Оптимізований знаковий крок\n";
}

int main() {
    advance_cursor(-5); // int задовольняє обидва концепти.
                        // Оскільки SignedIntegral нормалізується в (A && B),
                        // воно поглинає Integral (A).
                        // Викликається Кандидат 2 без жодної неоднозначності!
}
