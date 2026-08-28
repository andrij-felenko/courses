// Звичайне звільнення одиночного об'єкта
void operator delete(void* ptr) noexcept;

// Звичайне звільнення масиву
void operator delete[](void* ptr) noexcept;

// Non-throwing парний деалокатор одиночного об'єкта
void operator delete(void* ptr, const std::nothrow_t&) noexcept;

// Non-throwing парний деалокатор масиву
void operator delete[](void* ptr, const std::nothrow_t&) noexcept;
