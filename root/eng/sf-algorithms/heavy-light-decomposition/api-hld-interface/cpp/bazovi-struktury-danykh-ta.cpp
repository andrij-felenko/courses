#include <vector>
#include <cstdint>
#include <span>
#include <functional>
#include <concepts>
#include <stdexcept>

template <typename T>
concept MonoidValue = std::default_initializable<T> && std::copyable<T>;

template <MonoidValue ValueType = int64_t, typename CombineOp = std::plus<ValueType>>
class HeavyLightDecomposition {
private:
    struct SegmentTree;
    int node_count;
    int root_node;
    // Внутрішні плоскі контейнери топології та Segment Tree
};
