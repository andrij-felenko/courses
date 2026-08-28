struct Base {
    int id{1};
    virtual void print() const { std::cout << "Base\n"; }
};

struct Derived : Base {
    int extra_payload{42};
    void print() const override { std::cout << "Derived\n"; }
};

Derived d;
// Небезпека: Object Slicing!
Base b = static_cast<Base>(d);
b.print(); // Виводить "Base", а не "Derived"!
