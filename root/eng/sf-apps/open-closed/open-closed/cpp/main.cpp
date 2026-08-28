struct Shape {                       // завіса: стабільний контракт
    virtual double area() const = 0;
    virtual ~Shape() = default;
};

struct Circle : Shape {
    double r;
    double area() const override { return 3.14159265 * r * r; }
};

struct Rect : Shape {
    double w, h;
    double area() const override { return w * h; }
};

// Нова фігура — НОВИЙ клас, окремий файл. Нічого вище не відкрито:
struct Triangle : Shape {
    double base, height;
    double area() const override { return 0.5 * base * height; }
};

double total(const std::vector<Shape*> &shapes) {   // клієнт закритий
    double sum = 0.0;
    for (const Shape *s : shapes) sum += s->area();  // не знає про Triangle
    return sum;
}
