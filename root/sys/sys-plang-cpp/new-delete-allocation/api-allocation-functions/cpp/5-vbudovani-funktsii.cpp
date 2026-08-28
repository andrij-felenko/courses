// Placement new для одиночного об'єкта
void* operator new(std::size_t size, void* ptr) noexcept;

// Placement new для масиву
void* operator new[](std::size_t size, void* ptr) noexcept;

// Placement delete для одиночного об'єкта (викликається лише при винятку в конструкторі)
void operator delete(void* ptr, void* place) noexcept;

// Placement delete для масиву (викликається лише при винятку в конструкторі)
void operator delete[](void* ptr, void* place) noexcept;
