#include <iostream>
#include <iomanip>
#include <cstdint>

struct InterfaceA {
    virtual void methodA() = 0;
    virtual ~InterfaceA() = default; // Віртуальний деструктор
};

struct InterfaceB {
    virtual void methodB() = 0;
    // Помилка: деструктор НЕ є віртуальним
    ~InterfaceB() = default;
};

class ConcreteComponent : public InterfaceA, public InterfaceB {
    int payload_data[16]{};
public:
    ConcreteComponent() { payload_data[0] = 42; }
    void methodA() override { std::cout << "Виклик methodA()\n"; }
    void methodB() override { std::cout << "Виклик methodB()\n"; }
    ~ConcreteComponent() { std::cout << "Виклик ~ConcreteComponent()\n"; }
};

int main() {
    std::cout << "=== Дослідження зміщення покажчиків ===\n";
    ConcreteComponent* component = new ConcreteComponent();
    
    // Отримуємо поліморфні покажчики на різні інтерфейси одного об'єкта
    InterfaceA* ptrA = component;
    InterfaceB* ptrB = component;

    std::cout << std::hex << std::showbase;
    std::cout << "Адреса ConcreteComponent (початок блоку malloc): " << reinterpret_cast<uintptr_t>(component) << "\n";
    std::cout << "Адреса InterfaceA (зсув 0):                     " << reinterpret_cast<uintptr_t>(ptrA) << "\n";
    std::cout << "Адреса InterfaceB (зсув +8/+16):                " << reinterpret_cast<uintptr_t>(ptrB) << "\n";

    std::ptrdiff_t offset = reinterpret_cast<char*>(ptrB) - reinterpret_cast<char*>(component);
    std::cout << std::dec;
    std::cout << "Фізичний зсув покажчика InterfaceB: " << offset << " байтів\n";

    // Спроба видалення через InterfaceA (безпечно)
    delete ptrA;
    
    return 0;
}
