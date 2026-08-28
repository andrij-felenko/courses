template <typename T>
class SmartContainer {
public:
    void basic_action() {
        // Працює для будь-якого типу
    }

    void print_payload() {
        // Вимагає наявності operator<< для типу T!
        std::cout << payload_ << "\n";
    }

private:
    T payload_{};
};

struct OpaqueType {}; // Не має operator<<

void test_lazy() {
    SmartContainer<OpaqueType> c;
    c.basic_action(); // Працює бездоганно!
    
    // c.print_payload(); // Якщо розкоментувати — виникне помилка компіляції на Фазі 2!
}
