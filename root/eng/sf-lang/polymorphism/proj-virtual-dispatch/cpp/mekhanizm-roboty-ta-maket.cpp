#include <iostream>
#include <vector>
#include <memory>
#include <numbers>
#include <span>

/* Контракт таблиці віртуальних функцій */
struct ShapeVTable {
    void (*draw)(const void* self) noexcept;
    double (*area)(const void* self) noexcept;
};

/* Базова структура з vptr у нульовому зміщенні */
struct Shape {
    const ShapeVTable* vptr{nullptr};

    void draw() const noexcept {
        vptr->draw(this);
    }

    [[nodiscard]] double area() const noexcept {
        return vptr->area(this);
    }
};

/* Конкретний тип Коло */
struct Circle {
    Shape base;
    double radius{0.0};

    explicit Circle(double r) noexcept : radius(r) {
        static constexpr ShapeVTable vtable{
            .draw = [](const void* self) noexcept {
                const auto* c = static_cast<const Circle*>(self);
                (void)c;
            },
            .area = [](const void* self) noexcept -> double {
                const auto* c = static_cast<const Circle*>(self);
                return std::numbers::pi * c->radius * c->radius;
            }
        };
        base.vptr = &vtable;
    }
};

/* Поліморфна функція, що працює з діапазоном покажчиків */
[[nodiscard]] double compute_total_area(std::span<const Shape* const> shapes) noexcept {
    double total = 0.0;
    for (const auto* s : shapes) {
        total += s->area();
    }
    return total;
}
