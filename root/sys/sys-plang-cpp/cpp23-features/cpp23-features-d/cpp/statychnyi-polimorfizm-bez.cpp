struct Printable {
    template <typename Self>
    void print(this const Self& self) {
        // self має тип фактичного нащадка, а не Printable
        std::println("Об'єкт: {}", self.to_string());
    }
};

struct User : Printable {
    std::string name;
    std::string to_string() const { return name; }
};

struct Device : Printable {
    int id;
    std::string to_string() const { return std::to_string(id); }
};
