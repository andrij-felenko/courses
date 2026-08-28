#include <memory>
#include <functional>

template <typename K, typename V>
struct TNode {
    const K                       key;
    const V                       val;
    const std::shared_ptr<TNode>  left;
    const std::shared_ptr<TNode>  right;
    const int                     size;   // кількість вузлів у цьому піддереві (з собою)

    TNode(K k, V v, std::shared_ptr<TNode> l, std::shared_ptr<TNode> r)
        : key(std::move(k)), val(std::move(v)),
          left(std::move(l)), right(std::move(r)),
          size(1 + sz(left) + sz(right)) {}

    // розмір піддерева, стійкий до nullptr (порожнє піддерево має розмір 0)
    static int sz(const std::shared_ptr<TNode>& t) { return t ? t->size : 0; }
};

template <typename K, typename V>
using Tree = std::shared_ptr<TNode<K, V>>;

// Фабрика вузла — коротший запис make_shared. Розмір рахується в конструкторі.
template <typename K, typename V>
Tree<K, V> mk(K k, V v, Tree<K, V> l, Tree<K, V> r) {
    return std::make_shared<TNode<K, V>>(std::move(k), std::move(v),
                                         std::move(l), std::move(r));
}
