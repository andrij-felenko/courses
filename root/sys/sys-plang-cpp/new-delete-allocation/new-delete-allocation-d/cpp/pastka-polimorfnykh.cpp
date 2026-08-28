struct Base {
    int x;
    virtual ~Base() = default;
};

struct Derived : Base {
    int y;
    int z;
};

Base* array = new Derived[10]; // Небезпечно!
