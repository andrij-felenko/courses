template <typename Derived>
struct Relational {
    friend bool operator!=(const Derived& lhs, const Derived& rhs) {
        return !(lhs == rhs);
    }
    friend bool operator>(const Derived& lhs, const Derived& rhs) {
        return rhs < lhs;
    }
    friend bool operator<=(const Derived& lhs, const Derived& rhs) {
        return !(rhs < lhs);
    }
    friend bool operator>=(const Derived& lhs, const Derived& rhs) {
        return !(lhs < rhs);
    }
};

class Distance : public Relational<Distance> {
public:
    explicit Distance(double meters) : meters_(meters) {}

    friend bool operator==(const Distance& lhs, const Distance& rhs) {
        return lhs.meters_ == rhs.meters_;
    }
    friend bool operator<(const Distance& lhs, const Distance& rhs) {
        return lhs.meters_ < rhs.meters_;
    }

private:
    double meters_{0.0};
};
