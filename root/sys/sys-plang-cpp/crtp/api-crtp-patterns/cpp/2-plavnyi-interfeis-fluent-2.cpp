// C++23 Deducing This Fluent Builder
class ButtonBuilder23 {
public:
    template <typename Self>
    auto&& set_label(this Self&& self, std::string lbl) {
        self.label_ = std::move(lbl);
        return std::forward<Self>(self);
    }
};

class IconButton : public ButtonBuilder23 {
public:
    std::string label_;
};
