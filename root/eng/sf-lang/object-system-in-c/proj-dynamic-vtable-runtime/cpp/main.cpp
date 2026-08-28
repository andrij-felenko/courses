#include <iostream>
#include <memory>
#include <string>
#include <format>
#include <numbers>
#include <vector>

/* ── 1. Базовий клас Object з ідіоматичним C++ поліморфізмом ──────────────── */

class Object : public std::enable_shared_from_this<Object> {
public:
    virtual ~Object() = default;

    [[nodiscard]] virtual std::string to_string() const {
        return std::format("<Object at {}, use_count={}>", 
                           static_cast<const void*>(this), 
                           shared_from_this().use_count());
    }
};

/* ── 2. Проміжний абстрактний клас Shape ─────────────────────────────────── */

class Shape : public Object {
public:
    explicit Shape(std::string color) : m_color(std::move(color)) {}
    
    [[nodiscard]] virtual double area() const = 0;
    [[nodiscard]] virtual double perimeter() const = 0;
    [[nodiscard]] const std::string& color() const noexcept { return m_color; }

private:
    std::string m_color;
};

/* ── 3. Конкретний клас Circle ───────────────────────────────────────────── */

class Circle final : public Shape {
public:
    Circle(std::string color, double radius)
        : Shape(std::move(color)), m_radius(radius) {}

    [[nodiscard]] double area() const override {
        return std::numbers::pi * m_radius * m_radius;
    }

    [[nodiscard]] double perimeter() const override {
        return 2.0 * std::numbers::pi * m_radius;
    }

    [[nodiscard]] std::string to_string() const override {
        return std::format("Circle(color={}, radius={:.2f}, area={:.2f})", 
                           color(), m_radius, area());
    }

    [[nodiscard]] double radius() const noexcept { return m_radius; }

private:
    double m_radius;
};

/* ── 4. Демонстрація поліморфного використання ────────────────────────────── */

int main() {
    // std::make_shared автоматично створює блок керування з атомарним ref_count
    std::shared_ptr<Object> obj = std::make_shared<Circle>("Red", 5.0);

    // Поліморфний виклик через vtable компілятора
    std::cout << "Опис об'єкта: " << obj->to_string() << '\n';

    // Безпечне приведення вниз через dynamic_pointer_cast (RTTI)
    if (auto shape = std::dynamic_pointer_cast<Shape>(obj)) {
        std::cout << "Площа фігури: " << shape->area() << '\n';
        std::cout << "Периметр фігури: " << shape->perimeter() << '\n';
    }

    std::cout << "Поточний use_count: " << obj.use_count() << '\n';

    // Копіювання shared_ptr збільшує лічильник атомарно
    {
        std::shared_ptr<Object> alias = obj;
        std::cout << "У вкладеному блоці use_count: " << obj.use_count() << '\n';
    }
    std::cout << "Після виходу з блоку use_count: " << obj.use_count() << '\n';

    // Автоматичне викликання віртуального деструктора при виході з main
    return 0;
}
