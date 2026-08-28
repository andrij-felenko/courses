class Note : public Printable, public Comparable, public Taggable {
    std::string title_;
    std::unique_ptr<std::string> body_;

public:
    Note(std::string t, std::string b)
        : title_(std::move(t)), body_(std::make_unique<std::string>(std::move(b))) {}

    // прямий член: категорію несе сам вираз доступу
    template <class Self>
    auto&& title(this Self&& self) { return std::forward<Self>(self).title_; }

    // член за вказівником: розіменування кваліфікаторів не пам'ятає
    template <class Self>
    auto&& body(this Self&& self) { return std::forward_like<Self>(*self.body_); }

    std::string label() const { return title_ + " [" + tag + ']'; }
    const std::string& key() const { return title_; }
};
