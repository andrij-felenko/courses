template <class OuterAlloc, class... InnerAllocs>
class scoped_allocator_adaptor : public OuterAlloc {
public:
    using outer_allocator_type = OuterAlloc;
    using inner_allocator_type = /* наступний рівень або сам scoped_allocator */;

    // Конструктори
    scoped_allocator_adaptor();
    template <class OuterA2>
    explicit scoped_allocator_adaptor(OuterA2&& outerAlloc, const InnerAllocs&... innerAllocs) noexcept;

    // Доступ до алокаторів рівнів
    outer_allocator_type& outer_allocator() noexcept;
    const outer_allocator_type& outer_allocator() const noexcept;
    inner_allocator_type& inner_allocator() noexcept;
    const inner_allocator_type& inner_allocator() const noexcept;

    // Конструювання з автоматичним розгортанням пар і кортежів
    template <class T, class... Args>
    void construct(T* p, Args&&... args);

    template <class T1, class T2, class... Args1, class... Args2>
    void construct(std::pair<T1, T2>* p,
                   std::piecewise_construct_t,
                   std::tuple<Args1...> x,
                   std::tuple<Args2...> y);
};
