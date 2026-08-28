using GenericFunc = void (*)();
using SpecificFunc = int (*)(double, int);

SpecificFunc real_func = [](double d, int i) -> int { return static_cast<int>(d) + i; };

// Збереження покажчика у загальному реєстрі функцій:
GenericFunc stored = reinterpret_cast<GenericFunc>(real_func);

// НЕВИЗНАЧЕНА ПОВЕДІНКА: прямий виклик через неправильну сигнатуру!
// stored(); // UB: порушення конвенції виклику (Calling Convention Mismatch)

// Єдиний законний спосіб — приведення назад до точного вихідного типу:
auto restored = reinterpret_cast<SpecificFunc>(stored);
int result = restored(3.14, 10); // Валідно!
