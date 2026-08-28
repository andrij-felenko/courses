#include <iostream>
#include <iomanip>
#include <cstdint>
#include <cstddef>

class BaseA {
public:
    virtual void funcA() { std::cout << "BaseA::funcA\n"; }
    int a_val{100};
};

class BaseB {
public:
    virtual void funcB() { std::cout << "BaseB::funcB\n"; }
    int b_val{200};
};

class Derived : public BaseA, public BaseB {
public:
    void funcA() override { 
        std::cout << "Derived::funcA виконано (d_val = " << d_val << ")\n"; 
    }
    void funcB() override { 
        std::cout << "Derived::funcB виконано (d_val = " << d_val << ")\n"; 
    }
    int d_val{300};
};

int main() {
    Derived obj;
    Derived* p_derived = &obj;

    // Upcast: компілятор неявно генерує арифметику вказівників
    BaseA* p_a = static_cast<BaseA*>(p_derived);
    BaseB* p_b = static_cast<BaseB*>(p_derived);

    std::cout << "=== Двійкова розкладка об'єкта в C++ ===\n";
    std::cout << "Розмір Derived: " << sizeof(Derived) << " байтів\n";
    std::cout << "Адреса Derived: " << static_cast<void*>(p_derived) << "\n";
    std::cout << "Адреса BaseA*:  " << static_cast<void*>(p_a) 
              << " (Δ = " << reinterpret_cast<uintptr_t>(p_a) - reinterpret_cast<uintptr_t>(p_derived) << " B)\n";
    std::cout << "Адреса BaseB*:  " << static_cast<void*>(p_b) 
              << " (Δ = +" << reinterpret_cast<uintptr_t>(p_b) - reinterpret_cast<uintptr_t>(p_derived) << " B)\n";

    // Порівняння приведень типів
    BaseB* bad_b = reinterpret_cast<BaseB*>(p_derived);
    std::cout << "\n=== Порівняння безпеки кастингів ===\n";
    std::cout << "static_cast<BaseB*>:      читає b_val = " << p_b->b_val << " (коректно)\n";
    std::cout << "reinterpret_cast<BaseB*>: читає сміття замість b_val = " << bad_b->b_val << " (помилка зсуву!)\n";

    // Виклики віртуальних методів
    p_a->funcA();
    p_b->funcB(); // Виклик через secondary vtable з автоматичним thunk

    return 0;
}
