#include <iostream>
#include <memory>
#include <string>
#include <vector>

/* Демонстрація помилки та виправлення в C++ */
class BadBase {
public:
    int id{0};
    ~BadBase() { std::cout << "[BadBase] Деструктор базового класу\n"; }
};

class BadDerived : public BadBase {
public:
    std::vector<int> data;
    BadDerived() : data(10000, 42) {}
    ~BadDerived() { std::cout << "[BadDerived] Деструктор нащадка\n"; }
};

class GoodBase {
public:
    int id{0};
    /* Віртуальний деструктор гарантує виклик деструктора нащадка */
    virtual ~GoodBase() = default;
};

class GoodDerived : public GoodBase {
public:
    std::vector<int> data;
    GoodDerived() : data(10000, 42) {}
    ~GoodDerived() override { std::cout << "[GoodDerived] Деструктор нащадка (очищено 40 KB)\n"; }
};

int main() {
    std::cout << "--- Тест 1: Невіртуальний деструктор (витік) ---\n";
    BadBase *bad = new BadDerived();
    delete bad; // ВИКЛИКАЄТЬСЯ лише ~BadBase()! data витікає.

    std::cout << "\n--- Тест 2: Віртуальний деструктор + RAII (безпечно) ---\n";
    std::unique_ptr<GoodBase> good = std::make_unique<GoodDerived>();
    // Автоматично і коректно викличе ~GoodDerived(), а потім ~GoodBase()
    return 0;
}
