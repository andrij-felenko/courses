struct Printable {
    void print(this const auto& self) {          // self — тип НАЩАДКА
        std::cout << self.label() << '\n';       // label() оголошує нащадок
    }
};

struct Comparable {
    template <class Self>
    bool operator==(this const Self& self, const Self& other) {
        return self.key() == other.key();
    }
};

struct Taggable {
    std::string tag;

    template <class Self>
    auto&& with_tag(this Self&& self, std::string t) {
        self.tag = std::move(t);
        return std::forward<Self>(self);         // віддає НАЩАДКА, не Taggable
    }
};
