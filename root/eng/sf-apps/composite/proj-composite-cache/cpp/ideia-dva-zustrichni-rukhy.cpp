#include <vector>
#include <memory>
#include <limits>
#include <algorithm>

struct Rect {
    double minX, minY, maxX, maxY;
    static Rect empty() {                        // «нескінченно малий» бокс
        double inf = std::numeric_limits<double>::infinity();
        return { inf, inf, -inf, -inf };
    }
    void unite(const Rect& r) {                  // розширити себе іншим боксом
        minX = std::min(minX, r.minX);  minY = std::min(minY, r.minY);
        maxX = std::max(maxX, r.maxX);  maxY = std::max(maxY, r.maxY);
    }
};

class Group;                                     // попереднє оголошення для parent

class Shape {
public:
    Group* parent = nullptr;                     // НЕ-власне посилання вгору
    virtual ~Shape() = default;
    virtual Rect bounds() = 0;
};

class Rectangle : public Shape {
    double x, y, w, h;
public:
    Rectangle(double x, double y, double w, double h) : x(x), y(y), w(w), h(h) {}
    Rect bounds() override { return { x, y, x + w, y + h }; }   // листок: прямий рахунок
    void moveTo(double nx, double ny);           // тіло нижче — треба повне визначення Group
};

class Group : public Shape {
    std::vector<std::unique_ptr<Shape>> children;   // композит ВОЛОДІЄ дітьми
    bool dirty = true;
    Rect cached = Rect::empty();
public:
    void add(std::unique_ptr<Shape> child) {
        child->parent = this;
        children.push_back(std::move(child));
        invalidate();                            // структура змінилась
    }

    void remove(Shape* child) {
        auto it = std::find_if(children.begin(), children.end(),
                               [&](auto& c) { return c.get() == child; });
        if (it == children.end()) return;
        child->parent = nullptr;                 // спершу від'єднуємо…
        children.erase(it);                      // …бо erase тут-таки й знищить об'єкт
        invalidate();                            // видалення могло стиснути бокс
    }

    Rect bounds() override {
        if (dirty) {                             // лінивий перерахунок — лише коли брудні
            Rect box = Rect::empty();
            for (auto& c : children) box.unite(c->bounds());   // чисті діти — O(1)
            cached = box;
            dirty = false;
        }
        return cached;                           // чистий — миттєво, O(1)
    }

    void invalidate() {                          // себе й пращурів — у брудні, зі зупинкою
        Group* g = this;
        while (g && !g->dirty) {                 // уже брудний → вище теж брудні
            g->dirty = true;
            g = g->parent;
        }
    }
};

void Rectangle::moveTo(double nx, double ny) {
    x = nx; y = ny;
    if (parent) parent->invalidate();            // ← зсув ЛИСТКА теж псує кеш групи!
}
