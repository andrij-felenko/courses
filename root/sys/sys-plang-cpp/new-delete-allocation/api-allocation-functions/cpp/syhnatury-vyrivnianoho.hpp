#include <new>

// Вирівняне виділення одиночного об'єкта (викидає std::bad_alloc)
void* operator new(std::size_t size, std::align_val_t alignment);

// Вирівняне виділення масиву (викидає std::bad_alloc)
void* operator new[](std::size_t size, std::align_val_t alignment);

// Вирівняне non-throwing виділення одиночного об'єкта
void* operator new(std::size_t size, std::align_val_t alignment, const std::nothrow_t&) noexcept;

// Вирівняне non-throwing виділення масиву
void* operator new[](std::size_t size, std::align_val_t alignment, const std::nothrow_t&) noexcept;
