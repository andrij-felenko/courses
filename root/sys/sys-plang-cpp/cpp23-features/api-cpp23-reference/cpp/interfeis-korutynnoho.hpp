namespace std {

template <class Ref, class V = void, class Allocator = void>
class generator : public ranges::view_interface<generator<Ref, V, Allocator>> {
public:
    using yielded = conditional_t<is_reference_v<Ref>, Ref, const Ref&>;
    using value_type = conditional_t<is_void_v<V>, remove_cvref_t<Ref>, V>;
    using reference = conditional_t<is_reference_v<Ref>, Ref, value_type>;

    class promise_type {
    public:
        generator get_return_object() noexcept;
        suspend_always initial_suspend() noexcept;
        suspend_always final_suspend() noexcept;

        suspend_always yield_value(yielded val) noexcept;
        auto yield_value(const remove_reference_t<yielded>& val)
            requires is_rvalue_reference_v<yielded>;

        template <class R, class Alloc>
            requires same_as<ranges::range_value_t<R>, value_type>
        auto yield_value(ranges::elements_of<R, Alloc> r) noexcept;

        void return_void() noexcept;
        void unhandled_exception();
    };

    generator(const generator&) = delete;
    generator(generator&& other) noexcept;
    generator& operator=(generator&& other) noexcept;
    ~generator();

    struct iterator {
        using value_type = generator::value_type;
        using difference_type = ptrdiff_t;
        using iterator_concept = input_iterator_tag;

        iterator& operator++();
        void operator++(int);
        reference operator*() const noexcept;
        bool operator==(default_sentinel_t) const noexcept;
    };

    iterator begin();
    default_sentinel_t end() noexcept;
};

} // namespace std
