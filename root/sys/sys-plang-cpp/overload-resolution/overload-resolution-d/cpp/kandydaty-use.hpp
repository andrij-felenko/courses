struct Base {
    void log(int n);
    void log(const char* s);
};

struct Derived : Base {
    void log(double d);      // ховає ОБИДВА log із Base
};

Derived d;
d.log("привіт");             // помилка: єдиний кандидат — log(double)
