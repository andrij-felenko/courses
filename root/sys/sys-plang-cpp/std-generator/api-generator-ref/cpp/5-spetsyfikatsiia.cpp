namespace std::ranges {
    template<range R, class Alloc = allocator<char>>
    struct elements_of {
        [[no_unique_address]] R range;
        [[no_unique_address]] Alloc allocator = Alloc();
    };

    template<class R>
    elements_of(R&&) -> elements_of<R>;

    template<class R, class Alloc>
    elements_of(R&&, Alloc) -> elements_of<R, Alloc>;
}
