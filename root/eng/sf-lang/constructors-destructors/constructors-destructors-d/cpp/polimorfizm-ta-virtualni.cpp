class Base {
public:
    ~Base() { /* Не віртуальний! */ }
};

class Derived : public Base {
    int* large_buffer_;
public:
    Derived() : large_buffer_(new int[10000]) {}
    ~Derived() { delete[] large_buffer_; }
};

void cleanup(Base* ptr) {
    delete ptr; // Фатальна помилка: статичне зв'язування!
}
