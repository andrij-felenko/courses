struct DerivedWithUsing : public Base {
    // Вносимо всі перевантаження print з Base у область видимості DerivedWithUsing:
    using Base::print;

    // Додаємо власне перевантаження:
    void print(double value) {
        std::cout << "DerivedWithUsing::print(double): " << value << '\n';
    }
};

int main() {
    DerivedWithUsing d;
    d.print(3.14);  // ✓ DerivedWithUsing::print(double)
    d.print(42);    // ✓ Base::print(int) — точний збіг!
    d.print("hi");  // ✓ Base::print(string_view) — точний збіг!
}
