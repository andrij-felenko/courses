#include <concepts>

struct GenericBase {
    template <typename T>
    void process(T val) {
        std::cout << "GenericBase::process(загальний шаблон)\n";
    }
};

struct ConstrainedDerived : public GenericBase {
    using GenericBase::process;

    // Спеціалізоване перевантаження з концептом:
    template <std::integral T>
    void process(T val) {
        std::cout << "ConstrainedDerived::process(цілочисельний концепт)\n";
    }
};

void test_constraints() {
    ConstrainedDerived d;
    d.process(42);   // Викликає ConstrainedDerived::process (більш обмежений кандидат!)
    d.process(3.14); // Викликає GenericBase::process (обмеження integral не виконано)
}
