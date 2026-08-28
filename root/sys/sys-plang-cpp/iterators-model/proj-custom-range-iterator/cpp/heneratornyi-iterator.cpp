class FibonacciIterator {
public:
    using iterator_concept  = std::input_iterator_tag;
    using iterator_category = std::input_iterator_tag;
    using value_type        = uint64_t;
    using difference_type   = std::ptrdiff_t;
    using pointer           = const uint64_t*;
    using reference         = uint64_t;

    FibonacciIterator() = default;

    constexpr uint64_t operator*() const {
        return a_;
    }

    constexpr FibonacciIterator& operator++() {
        uint64_t next = a_ + b_;
        a_ = b_;
        b_ = next;
        return *this;
    }

    constexpr FibonacciIterator operator++(int) {
        FibonacciIterator tmp = *this;
        ++(*this);
        return tmp;
    }

    friend bool operator==(const FibonacciIterator& lhs, const FibonacciIterator& rhs) {
        return lhs.a_ == rhs.a_ && lhs.b_ == rhs.b_;
    }

private:
    uint64_t a_{0};
    uint64_t b_{1};
};
