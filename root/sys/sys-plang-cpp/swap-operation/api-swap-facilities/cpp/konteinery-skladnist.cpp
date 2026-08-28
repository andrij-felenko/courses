// A — послідовні контейнери й рядок
noexcept(allocator_traits<Allocator>::propagate_on_container_swap::value ||
         allocator_traits<Allocator>::is_always_equal::value)

// B — впорядковані асоціативні
noexcept(allocator_traits<Allocator>::is_always_equal::value &&
         is_nothrow_swappable_v<Compare>)

// C — невпорядковані
noexcept(allocator_traits<Allocator>::is_always_equal::value &&
         is_nothrow_swappable_v<Hash> && is_nothrow_swappable_v<Pred>)
