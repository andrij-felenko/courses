// Звичайне вирівняне звільнення одиночного об'єкта
void operator delete(void* ptr, std::align_val_t alignment) noexcept;

// Звичайне вирівняне звільнення масиву
void operator delete[](void* ptr, std::align_val_t alignment) noexcept;

// Non-throwing вирівняне звільнення одиночного об'єкта
void operator delete(void* ptr, std::align_val_t alignment, const std::nothrow_t&) noexcept;

// Non-throwing вирівняне звільнення масиву
void operator delete[](void* ptr, std::align_val_t alignment, const std::nothrow_t&) noexcept;

// Розмірне вирівняне звільнення одиночного об'єкта (C++17)
void operator delete(void* ptr, std::size_t size, std::align_val_t alignment) noexcept;

// Розмірне вирівняне звільнення масиву (C++17)
void operator delete[](void* ptr, std::size_t size, std::align_val_t alignment) noexcept;
