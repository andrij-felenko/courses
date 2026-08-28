template<typename T, size_t Capacity>
class RingBufferIterator {
public:
    using iterator_concept  = std::random_access_iterator_tag;
    using iterator_category = std::random_access_iterator_tag;
    using value_type        = T;
    using difference_type   = std::ptrdiff_t;
    using pointer           = T*;
    using reference         = T&;

    RingBufferIterator(T* buffer_base, size_t head_index, difference_type pos)
        : base_(buffer_base), pos_(pos) {}

    reference operator*() const {
        return base_[(pos_) % Capacity];
    }

    pointer operator->() const {
        return &base_[(pos_) % Capacity];
    }

    RingBufferIterator& operator++() {
        ++pos_;
        return *this;
    }

    RingBufferIterator operator++(int) {
        RingBufferIterator tmp = *this;
        ++(*this);
        return tmp;
    }

    RingBufferIterator& operator+=(difference_type n) {
        pos_ += n;
        return *this;
    }

    friend difference_type operator-(const RingBufferIterator& a, const RingBufferIterator& b) {
        return a.pos_ - b.pos_;
    }

    friend bool operator==(const RingBufferIterator& a, const RingBufferIterator& b) {
        return a.pos_ == b.pos_;
    }

    friend auto operator<=>(const RingBufferIterator& a, const RingBufferIterator& b) {
        return a.pos_ <=> b.pos_;
    }

private:
    T* base_{nullptr};
    difference_type pos_{0};
};
