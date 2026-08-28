namespace geo {
    class IntervalTreeIterator {
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type        = Interval;
        using difference_type   = std::ptrdiff_t;
        using pointer           = const Interval*;
        using reference         = const Interval&;

        IntervalTreeIterator() noexcept = default;
        explicit IntervalTreeIterator(const IntervalNode* root) noexcept;

        reference operator*() const noexcept;
        pointer operator->() const noexcept;
        IntervalTreeIterator& operator++() noexcept;
        bool operator==(const IntervalTreeIterator& other) const noexcept;
    };
}
