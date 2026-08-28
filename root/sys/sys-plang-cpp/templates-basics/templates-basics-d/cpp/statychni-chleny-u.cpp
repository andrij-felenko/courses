template <typename T>
struct InstanceCounter {
    static inline int count = 0;
    InstanceCounter() { ++count; }
};

void demo_static() {
    InstanceCounter<int> a, b;
    InstanceCounter<double> c;
    
    // InstanceCounter<int>::count == 2
    // InstanceCounter<double>::count == 1
}
