template <typename Derived>
class NumericOperations {
public:
    void increment() {
        // Статичний upcast без віртуальної таблиці та без витрат пам'яті
        static_cast<Derived*>(this)->add(1);
    }
};

class Counter : public NumericOperations<Counter> {
public:
    int value{0};
    void add(int n) { value += n; }
};
