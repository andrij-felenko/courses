namespace LibA {
    void process(double x) {
        std::cout << "LibA::process(double): " << x << '\n';
    }
}

// Глобальна функція:
void process(int x) {
    std::cout << "::process(int): " << x << '\n';
}

void test_using_declaration() {
    using LibA::process; // Вводить process(double) безпосередньо в область функції test_using_declaration
    process(10);         // Викликає LibA::process(10.0)! Глобальна process(int) ЗАТУЛЕНА.
}

void test_using_directive() {
    using namespace LibA; // Робить символи LibA видимими на рівні глобального простору (спільний предок)
    // process(10);       // ✗ ПОМИЛКА: неоднозначність (Ambiguity)!
                          // ::process(int) і LibA::process(double) змагаються на одному рівні!
}
