// Сучасний підхід C++23 (Deducing This)
struct Logger23 {
    // Перший параметр "this auto&& self" виводить точний тип викликача!
    void print_name(this const auto& self) {
        std::cout << self.get_name() << "\n";
    }
};

// Звичайне, нешаблонне успадкування!
class User : public Logger23 {
public:
    std::string get_name() const { return "UserObject"; }
};
