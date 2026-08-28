// Концептуальна внутрішня структура реалізації у бібліотеці STL
template <typename T, typename E>
class expected {
private:
    union {
        T val_;
        E unex_;
    };
    bool has_value_;
};
