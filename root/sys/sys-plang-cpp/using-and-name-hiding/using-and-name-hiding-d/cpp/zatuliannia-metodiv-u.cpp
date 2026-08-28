#include <iostream>
#include <string_view>

struct Base {
    void print(int value) {
        std::cout << "Base::print(int): " << value << '\n';
    }
    void print(std::string_view text) {
        std::cout << "Base::print(string_view): " << text << '\n';
    }
};

struct Derived : public Base {
    // Оголошення print(double) затуляє ВСІ перевантаження print у Base!
    void print(double value) {
        std::cout << "Derived::print(double): " << value << '\n';
    }
};

int main() {
    Derived d;
    d.print(3.14);    // ✓ Викликає Derived::print(double)
    d.print(42);      // ⚠ Неявно перетворює int на double -> Derived::print(42.0)
    // d.print("hi"); // ✗ ПОМИЛКА КОМПІЛЯЦІЇ: const char* не можна перетворити на double!
}
