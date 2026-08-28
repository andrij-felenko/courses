namespace lib {
    struct String { /* ... */ };
    std::ostream& operator<<(std::ostream&, const String&);
}

namespace app {
    void print(const lib::String& s) {
        std::cout << s;          // до правила: ім'я operator<< тут не видно
    }
}
