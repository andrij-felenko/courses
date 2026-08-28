template <typename Derived>
class EqualComparable {
public:
    friend bool operator!=(const Derived& lhs, const Derived& rhs) {
        return !(lhs == rhs);
    }
};

class Complex : public EqualComparable<Complex> {
public:
    bool operator==(const Complex& rhs) const {
        return re == rhs.re && im == rhs.im;
    }
private:
    double re{0.0};
    double im{0.0};
};
