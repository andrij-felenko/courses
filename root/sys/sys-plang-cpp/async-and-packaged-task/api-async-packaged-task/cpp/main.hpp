// 1. Конструктор за замовчуванням: створює об'єкт без спільного стану
packaged_task() noexcept;

// 2. Параметризований конструктор: приймає callable-об'єкт f
template< class F >
explicit packaged_task( F&& f );

// 3. Конструктор із підтримкою розподілювача пам'яті (вилучено в C++17)
template< class F, class Alloc >
packaged_task( std::allocator_arg_t, const Alloc& alloc, F&& f );

// 4. Конструктор переміщення: передає володіння спільним станом
packaged_task( packaged_task&& rhs ) noexcept;

// 5. Заборонений конструктор копіювання
packaged_task( const packaged_task& ) = delete;

// 6. Деструктор
~packaged_task();
