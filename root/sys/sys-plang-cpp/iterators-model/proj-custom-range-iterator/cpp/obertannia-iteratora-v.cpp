template<std::ranges::viewable_range Range>
class StrideView : public std::ranges::view_interface<StrideView<Range>> {
public:
    StrideView() = default;
    
    constexpr StrideView(Range&& range, std::ranges::range_difference_t<Range> stride)
        : range_(std::forward<Range>(range)), stride_(stride) {}

    constexpr auto begin() {
        return StrideIterator(std::ranges::begin(range_), stride_);
    }

    constexpr auto end() {
        auto end_it = std::ranges::end(range_);
        // Обчислення точної межі кінця з урахуванням кроку
        auto dist = std::ranges::distance(range_);
        auto remainder = dist % stride_;
        auto offset = dist - remainder;
        return StrideIterator(std::ranges::begin(range_) + offset, stride_);
    }

private:
    Range range_{};
    std::ranges::range_difference_t<Range> stride_{1};
};
