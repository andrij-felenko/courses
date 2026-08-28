// C++23 Deducing This
struct Printable23 {
    void print(this const auto& self) {
        std::cout << self.get_name() << "\n";
    }
};

class Item : public Printable23 {
public:
    std::string get_name() const { return "ItemA"; }
};
