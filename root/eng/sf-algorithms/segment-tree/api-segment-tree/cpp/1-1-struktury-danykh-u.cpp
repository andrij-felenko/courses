template <typename T, typename CombineOp = std::plus<T>>
class SegmentTree {
private:
    std::size_t n_;
    T identity_;
    CombineOp op_;
    std::vector<T> tree_;
};

template <typename T, typename CombineOp = std::plus<T>, typename LazyOp = std::plus<T>>
class LazySegmentTree {
private:
    std::size_t n_;
    std::vector<T> tree_;
    std::vector<T> lazy_;
};
