template <typename ValueType>
struct ImpNode {
    ValueType val;
    ValueType sum;
    int sz{1};
    bool rev{false};
    uint32_t priority;
    std::unique_ptr<ImpNode> left{nullptr};
    std::unique_ptr<ImpNode> right{nullptr};
};
