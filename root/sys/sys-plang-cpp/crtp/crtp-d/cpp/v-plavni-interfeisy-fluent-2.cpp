template <typename Derived>
class WindowCRTP {
public:
    Derived& set_width(int w) {
        Derived& self = *static_cast<Derived*>(this);
        self.width = w;
        return self;
    }
    int width{0};
};

class FancyWindow : public WindowCRTP<FancyWindow> {
public:
    FancyWindow& set_color(uint32_t c) {
        color = c;
        return *this;
    }
    uint32_t color{0};
};
