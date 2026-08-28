// Звичайне виділення одиночного об'єкта (викидає std::bad_alloc)
void* operator new(std::size_t size);

// Звичайне виділення масиву (викидає std::bad_alloc)
void* operator new[](std::size_t size);

// Non-throwing версія для одиночного об'єкта (повертає nullptr при помилці)
void* operator new(std::size_t size, const std::nothrow_t&) noexcept;

// Non-throwing версія для масиву (повертає nullptr при помилці)
void* operator new[](std::size_t size, const std::nothrow_t&) noexcept;
