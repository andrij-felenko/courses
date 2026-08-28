#include <experimental/propagate_const>

class Widget {
    struct Impl;
    std::experimental::propagate_const<std::unique_ptr<Impl>> pImpl_;

public:
    void mutate();
    void inspect() const {
        // pImpl_ автоматично розіменовується як const Impl*
    }
};
