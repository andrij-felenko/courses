// Проблема класичного спадкування:
class Window {
public:
    Window& set_width(int w) { width = w; return *this; }
    int width{0};
};

class FancyWindow : public Window {
public:
    FancyWindow& set_color(uint32_t c) { color = c; return *this; }
    uint32_t color{0};
};

// FancyWindow win;
// win.set_width(800).set_color(0xFF0000); // ПОМИЛКА: set_width повертає Window&!
