template <typename Derived>
class Base {
public:
    void interface() {
        // Приведення вказівника this до типу Derived* і виклик реалізації
        static_cast<Derived*>(this)->implementation();
    }
};

class Derived : public Base<Derived> {
public:
    void implementation() {
        // Конкретна реалізація у похідному класі
    }
};
