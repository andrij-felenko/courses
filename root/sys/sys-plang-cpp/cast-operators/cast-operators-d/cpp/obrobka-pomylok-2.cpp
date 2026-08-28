#include <typeinfo>
#include <iostream>

struct Shape { virtual ~Shape() = default; };
struct Circle : Shape { void draw_circle() {} };

void render_ref(Shape& shape) {
    try {
        // Оскільки «нульових посилань» не існує, невдача кидає виняток:
        Circle& circle = dynamic_cast<Circle&>(shape);
        circle.draw_circle();
    } catch (const std::bad_cast& e) {
        std::cerr << "Помилка приведення посилання: " << e.what() << '\n';
    }
}
