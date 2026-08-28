int main() {
    long long a = 42;
    long long m = 1000000007; // Відомий простий модуль

    std::cout << "Шукаємо обернений елемент для a = " << a << " за модулем m = " << m << "\n";

    try {
        long long invGcd = modInverseGcd(a, m);
        std::cout << "Результат (Евклід): " << invGcd << "\n";
        std::cout << "Перевірка: (" << a << " * " << invGcd << ") mod " << m << " = " 
                  << (a * invGcd) % m << "\n";
                  
        long long invFermat = modInverseFermat(a, m);
        std::cout << "Результат (Ферма) : " << invFermat << "\n";
        std::cout << "Перевірка: (" << a << " * " << invFermat << ") mod " << m << " = " 
                  << (a * invFermat) % m << "\n";
                  
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
    }

    return 0;
}
