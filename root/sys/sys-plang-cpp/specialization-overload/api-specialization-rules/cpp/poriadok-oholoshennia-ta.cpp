namespace core {
    template<typename T>
    struct Formatter; // Первинний шаблон у namespace core
}

// ВАЛІДНО: спеціалізація у просторі імен первинного шаблону
namespace core {
    template<>
    struct Formatter<int> { /* ... */ };
}

// ВАЛІДНО у C++11/C++14/C++17/C++20: явна кваліфікація з глобального простору
template<>
struct core::Formatter<double> { /* ... */ };
