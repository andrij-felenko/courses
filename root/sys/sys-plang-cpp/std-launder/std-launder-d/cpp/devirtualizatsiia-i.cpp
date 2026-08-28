#include <new>
#include <iostream>

struct Base {
    virtual void speak() const { std::cout << "Base\n"; }
    virtual ~Base() = default;
};

struct Dog : Base {
    void speak() const override { std::cout << "Гав!\n"; }
};

struct Cat : Base {
    void speak() const override { std::cout << "Няв!\n"; }
};

void test_animals() {
    alignas(Dog) alignas(Cat) std::byte storage[sizeof(Dog)];
    
    // Створюємо перший об'єкт Dog
    Base* animal = new (storage) Dog();
    animal->speak(); // Оптимізатор девіртуалізує це у прямий виклик Dog::speak() -> "Гав!"

    animal->~Base();

    // Створюємо Cat у тому самому місці
    new (storage) Cat();

    // Звернення через старий вказівник animal:
    animal->speak(); // ДЕВІРТУАЛІЗАЦІЯ: оптимізатор може знову викликати Dog::speak()!
}
