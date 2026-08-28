struct Base1 {
    int a;
    virtual void f() {}
};

struct Base2 {
    int b;
    virtual void g() {}
};

struct Derived : Base1, Base2 {
    int c;
};
