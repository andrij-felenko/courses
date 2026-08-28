// ПОМИЛКА: Два покажчики та дві алокації в купі на один об'єкт
class Base {
    struct BaseImpl;
    std::unique_ptr<BaseImpl> pImpl_;
};

class Derived : public Base {
    struct DerivedImpl;
    std::unique_ptr<DerivedImpl> pDerivedImpl_; // ДРУГА алокація в купі!
};
