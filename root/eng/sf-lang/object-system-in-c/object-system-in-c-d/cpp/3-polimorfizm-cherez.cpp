#include <iostream>
#include <string>
#include <vector>
#include <memory>

// Базовий поліморфний клас: компілятор автоматично генерує прихований vptr
class Widget {
public:
    Widget(int x, int y) : m_x(x), m_y(y) {}
    virtual ~Widget() = default;

    virtual void draw() const {
        std::cout << "Base Widget drawing at (" << m_x << ", " << m_y << ")\n";
    }

    [[nodiscard]] int x() const noexcept { return m_x; }
    [[nodiscard]] int y() const noexcept { return m_y; }

private:
    int m_x;
    int m_y;
};

// Клас-нащадок з явним перевизначенням методу
class Button : public Widget {
public:
    Button(int x, int y, std::string label)
        : Widget(x, y), m_label(std::move(label)) {}

    void draw() const override {
        std::cout << "Button drawing [" << m_label << "] at (" 
                  << x() << ", " << y() << ")\n";
    }

private:
    std::string m_label;
};

// Поліморфна функція
void render_scene(const Widget& w) {
    w.draw(); // Динамічна диспетчеризація через vtable компілятора
}

int main() {
    auto base_obj = std::make_unique<Widget>(10, 20);
    auto btn_obj = std::make_unique<Button>(100, 200, "Submit");

    render_scene(*base_obj);
    render_scene(*btn_obj);
    return 0;
}
