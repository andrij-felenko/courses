#include <iostream>
#include <memory>
#include <vector>

struct Shape {
    virtual ~Shape() = default;
    virtual void draw() const = 0; // Динамічне зв'язування
};

struct Circle final : Shape {
    void draw() const override {
        // Конкретне коло
    }
};

// Статичне зв'язування: шаблонна функція інстанціюється для конкретного типу
template <typename T>
void render_static(const T& shape) {
    shape.draw(); // Прямий виклик з можливістю повного інлайнінгу
}

// Динамічне зв'язування: виклик через абстрактний інтерфейс
void render_dynamic(const Shape& shape) {
    shape.draw(); // Непрямий виклик через vtable
}
