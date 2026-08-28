class Base {
public:
    Base() {
        setup(); // Виклик невіртуального методу предка
    }

    void setup() {
        // Непрямий виклик: на момент виконання setup() vptr вказує на vtable for Base!
        draw(); 
    }

    virtual void draw() = 0;
    virtual ~Base() = default;
};

class Derived : public Base {
public:
    void draw() override {
        std::cout << "Derived::draw()\n";
    }
};
