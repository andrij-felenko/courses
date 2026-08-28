// Base.h
class Base {
public:
    Base();
    virtual ~Base();
    void base_action();

protected:
    struct Impl;
    // Захищений конструктор для спадкоємців
    explicit Base(std::unique_ptr<Impl> impl);
    std::unique_ptr<Impl> pImpl_;
};

// Derived.h
class Derived : public Base {
public:
    Derived();
    ~Derived() override;
    void derived_action();
};

// Derived.cpp
#include "Derived.h"
#include "Base.h"

struct Derived::Impl : public Base::Impl {
    int extra_field_{42};
};

Derived::Derived() 
    : Base(std::make_unique<Derived::Impl>()) {}

Derived::~Derived() = default;

void Derived::derived_action() {
    // Безпечний статичний каст, оскільки тип Impl гарантовано Derived::Impl
    auto* impl = static_cast<Derived::Impl*>(pImpl_.get());
    impl->extra_field_ += 10;
}
