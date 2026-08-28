// ── Абстракція: ЩО малюємо (вісь 2) ───────────────────────────
class Shape {
public:
    Renderer* r;                              // ← МІСТ до реалізації
    explicit Shape(Renderer* r) : r(r) {}
    virtual void draw() = 0;
    virtual ~Shape() = default;
};

class Circle : public Shape {
    double cx, cy, rad;
public:
    Circle(Renderer* r, double cx, double cy, double rad)
        : Shape(r), cx(cx), cy(cy), rad(rad) {}
    void draw() override { r->ellipse(cx, cy, rad, rad); }
};

class Rect : public Shape {
    double x, y, w, h;
public:
    Rect(Renderer* r, double x, double y, double w, double h)
        : Shape(r), x(x), y(y), w(w), h(h) {}
    void draw() override {
        r->polyline({{x, y}, {x + w, y}, {x + w, y + h}, {x, y + h}}, true);
    }
};

class Triangle : public Shape {
    std::vector<Point> pts;
public:
    Triangle(Renderer* r, Point a, Point b, Point c) : Shape(r), pts{a, b, c} {}
    void draw() override { r->polyline(pts, true); }
};

class Star : public Shape {
    double cx, cy, outer, inner;
    int points;
public:
    Star(Renderer* r, double cx, double cy, double outer, double inner, int points = 5)
        : Shape(r), cx(cx), cy(cy), outer(outer), inner(inner), points(points) {}
    void draw() override {
        std::vector<Point> pts;
        for (int i = 0; i < points * 2; ++i) {
            double rad = (i % 2 == 0) ? outer : inner;
            double t = std::numbers::pi * i / points - std::numbers::pi / 2;
            pts.push_back({cx + rad * std::cos(t), cy + rad * std::sin(t)});
        }
        r->polyline(pts, true);               // геометрія зірки — ОДИН раз на всі рушії
    }
};

class Scene {
    Renderer* r;
    std::vector<std::unique_ptr<Shape>> shapes;
public:
    Scene(Renderer* r, std::vector<std::unique_ptr<Shape>> shapes)
        : shapes(std::move(shapes)) { use(r); }
    void use(Renderer* r) {                   // ← жива заміна рушія на льоту
        this->r = r;
        for (auto& s : shapes) s->r = r;
    }
    std::string draw(int w, int h) {
        r->begin(w, h);
        for (auto& s : shapes) s->draw();
        return r->end();
    }
};
