// C++17 CRTP Fluent Builder
template <typename Derived>
class ButtonBuilderCRTP {
public:
    Derived& set_label(std::string lbl) {
        Derived& self = *static_cast<Derived*>(this);
        self.label_ = std::move(lbl);
        return self;
    }
};

class IconButton : public ButtonBuilderCRTP<IconButton> {
public:
    std::string label_;
};
