struct BaseCalculator {
    int compute(int x) { return x * 2; }
    double compute(double x) { return x * 2.0; }
};

struct AdvancedCalculator : public BaseCalculator {
    using BaseCalculator::compute;

    // Точний збіг сигнатури з BaseCalculator::compute(int):
    int compute(int x) { return x * 3; }
};

int main() {
    AdvancedCalculator calc;
    std::cout << calc.compute(10);   // Виведе 30 (AdvancedCalculator::compute)
    std::cout << calc.compute(2.5);  // Виведе 5.0 (BaseCalculator::compute)
}
