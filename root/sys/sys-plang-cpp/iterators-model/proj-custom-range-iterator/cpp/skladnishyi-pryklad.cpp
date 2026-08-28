template<typename It1, typename It2>
class ZipIterator {
public:
    using value_type = std::tuple<std::iter_value_t<It1>, std::iter_value_t<It2>>;
    using reference  = std::tuple<std::iter_reference_t<It1>, std::iter_reference_t<It2>>;
    using difference_type = std::common_type_t<std::iter_difference_t<It1>, std::iter_difference_t<It2>>;
    using iterator_category = std::forward_iterator_tag;

    ZipIterator(It1 it1, It2 it2) : it1_(it1), it2_(it2) {}

    reference operator*() const {
        return reference(*it1_, *it2_);
    }

    ZipIterator& operator++() {
        ++it1_;
        ++it2_;
        return *this;
    }

    friend bool operator==(const ZipIterator& lhs, const ZipIterator& rhs) {
        return lhs.it1_ == rhs.it1_ || lhs.it2_ == rhs.it2_;
    }

private:
    It1 it1_;
    It2 it2_;
};
