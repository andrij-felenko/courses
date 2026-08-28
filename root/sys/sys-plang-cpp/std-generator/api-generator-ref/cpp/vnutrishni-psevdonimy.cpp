template<class Ref, class V, class Allocator>
class generator {
public:
    using yielded = std::conditional_t<std::is_reference_v<Ref>, Ref, const Ref&>;
    using value_type = std::conditional_t<std::is_void_v<V>, std::remove_cvref_t<Ref>, V>;
    using difference_type = std::ptrdiff_t;
    using allocator_type = Allocator;
    
    class promise_type;
    class iterator;
};
