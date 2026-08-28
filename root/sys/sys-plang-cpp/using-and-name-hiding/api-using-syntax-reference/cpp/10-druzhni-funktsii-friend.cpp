class Fraction {
private:
    int num_, den_;
public:
    Fraction(int n, int d) : num_(n), den_(d) {}

    // Прихований друг: оголошено й визначено всередині класу
    friend Fraction operator+(const Fraction& a, const Fraction& b) {
        return Fraction(a.num_ * b.den_ + b.num_ * a.den_, a.den_ * b.den_);
    }
};
