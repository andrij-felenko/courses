// C++17 CRTP
template <typename Derived>
struct PrintableCRTP {
    void print() const {
        const auto& self = *static_cast<const Derived*>(this);
        std::cout << self.get_name() << "\n";
    }
};

class Item : public PrintableCRTP<Item> {
public:
    std::string get_name() const { return "ItemA"; }
};
