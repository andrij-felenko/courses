#include <format>
#include <iostream>
#include <memory>
#include <string>

// Реалізація: ЯК фізично намалювати примітив (вісь 1)
struct Renderer {
    virtual std::string drawCircle(double x, double y, double r) const = 0;
    virtual ~Renderer() = default;
};

struct VectorRenderer : Renderer {
    std::string drawCircle(double x, double y, double r) const override {
        return std::format("<circle cx={} cy={} r={}/>", x, y, r);      // SVG
    }
};
struct RasterRenderer : Renderer {
    std::string drawCircle(double x, double y, double r) const override {
        return std::format("піксельне коло R={} у ({},{})", r, x, y);   // растр
    }
};

// Абстракція: ЩО малюємо; тримає рушій і делегує (вісь 2)
class Shape {
protected:
    std::shared_ptr<Renderer> r;              // ← міст до реалізації
public:
    explicit Shape(std::shared_ptr<Renderer> renderer) : r(std::move(renderer)) {}
    virtual std::string draw() const = 0;
    virtual ~Shape() = default;
};

class Circle : public Shape {
    double x, y, rad;
public:
    Circle(std::shared_ptr<Renderer> r, double x, double y, double rad)
        : Shape(std::move(r)), x(x), y(y), rad(rad) {}
    std::string draw() const override { return r->drawCircle(x, y, rad); }
};

int main() {
    Circle c(std::make_shared<VectorRenderer>(), 10, 10, 5);
    std::cout << c.draw() << '\n';   // <circle .../>  — векторний
    // той самий Circle з іншим рушієм: жодного нового класу
    std::cout << Circle(std::make_shared<RasterRenderer>(), 10, 10, 5).draw() << '\n';
}
