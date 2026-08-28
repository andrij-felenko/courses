// Класичний CRTP (C++98–C++20)
template <typename Derived>
struct LoggerCRTP {
    void print_name() const {
        const auto& self = *static_cast<const Derived*>(this);
        std::cout << self.get_name() << "\n";
    }
};

class User : public LoggerCRTP<User> {
public:
    std::string get_name() const { return "UserObject"; }
};
