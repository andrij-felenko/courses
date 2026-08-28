struct Base {
    int x;
};

struct Derived : Base {
    const int y;
};

void subobject_example() {
    alignas(Derived) std::byte buf[sizeof(Derived)];
    
    auto* d1 = new (buf) Derived{{1}, 2};
    Base* b = d1; // вказівник на підоб'єкт Base

    d1->~Derived();
    new (buf) Derived{{10}, 20};

    // Виклик std::launder(b) повертає Base*, що вказує на підоб'єкт Base нового Derived.
    Base* new_b = std::launder(b);
    
    // Чи можна робити static_cast<Derived*>(new_b)?
    // Так! Оскільки new_b тепер легально зв'язаний із новим об'єктом.
    Derived* new_d = static_cast<Derived*>(new_b);
    std::cout << new_d->y << '\n'; // 20
}
