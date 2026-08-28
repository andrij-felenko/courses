#include <cstddef>
#include <cstdint>
#include <iterator>

class FibonacciIterator {
public:
    using value_type = std::uint64_t;
    using difference_type = std::ptrdiff_t;
    using iterator_concept = std::input_iterator_tag;

    FibonacciIterator() : count_(0), a_(0), b_(1) {}
    FibonacciIterator(std::size_t limit) : count_(limit), a_(0), b_(1) {}

    std::uint64_t operator*() const { return a_; }

    FibonacciIterator& operator++() {
        auto next = a_ + b_;
        a_ = b_;
        b_ = next;
        if (count_ > 0) --count_;
        return *this;
    }

    bool operator==(const FibonacciIterator& other) const {
        return count_ == other.count_;
    }

private:
    std::size_t count_{0};
    std::uint64_t a_{0};
    std::uint64_t b_{1};
};
