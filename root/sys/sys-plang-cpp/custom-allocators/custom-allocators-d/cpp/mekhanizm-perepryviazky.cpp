template <typename T, typename Alloc>
class MyList {
    using Node = __list_node<T>;
    using NodeAlloc = typename std::allocator_traits<Alloc>::template rebind_alloc<Node>;
    using NodeTraits = std::allocator_traits<NodeAlloc>;

    NodeAlloc node_allocator_;

    Node* create_node(const T& value) {
        Node* p = NodeTraits::allocate(node_allocator_, 1);
        try {
            std::allocator_traits<Alloc>::construct(node_allocator_, std::addressof(p->value), value);
        } catch (...) {
            NodeTraits::deallocate(node_allocator_, p, 1);
            throw;
        }
        return p;
    }
};
