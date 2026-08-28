class BaseA {
public:
    virtual void opA();
    int a;
};

class BaseB {
public:
    virtual void opB();
    int b;
};

class Derived : public BaseA, public BaseB {
public:
    void opA() override;
    void opB() override;
    int d;
};
