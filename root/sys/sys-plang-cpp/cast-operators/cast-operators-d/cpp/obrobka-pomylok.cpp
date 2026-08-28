#include <iostream>

struct Shape { virtual ~Shape() = default; };
struct Circle : Shape { void draw_circle() {} };
struct Square : Shape { void draw_square() {} };

void render(Shape* shape) {
    // Якщо shape не є екземпляром Circle, dynamic_cast повертає nullptr
    if (auto* circle = dynamic_cast<Circle*>(shape)) {
        circle->draw_circle();
    } else {
        // Об'єкт належить до іншого підтипу
    }
}
