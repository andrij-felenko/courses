template <typename Storage>
void extract_and_run(Storage& s) {
    // Явне позначення виклику методу-шаблону:
    auto val1 = s.template get<int>(0);
    
    // Виклик через покажчик:
    Storage* s_ptr = &s;
    auto val2 = s_ptr->template get<double>(1);
}

// Використання template для вкладених шаблонів типів (Rebind):
template <typename Allocator>
struct AllocatorWrapper {
    // Вкладений шаблон Rebind всередині залежного алокатора:
    using OtherAlloc = typename Allocator::template rebind<double>::other;
};
