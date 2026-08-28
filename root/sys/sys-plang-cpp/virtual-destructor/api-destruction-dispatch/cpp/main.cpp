#include <new>
#include <cstddef>

// 1. Базові скалярні та масивні оператори (C++98)
void operator delete(void* ptr) noexcept;
void operator delete[](void* ptr) noexcept;

// 2. Оператори вивільнення з точним розміром (C++14 Sized Deallocation)
void operator delete(void* ptr, std::size_t size) noexcept;
void operator delete[](void* ptr, std::size_t size) noexcept;

// 3. Оператори з вирівнюванням (C++17 Aligned Deallocation)
void operator delete(void* ptr, std::align_val_t al) noexcept;
void operator delete[](void* ptr, std::align_val_t al) noexcept;

// 4. Комбіновані оператори з розміром та вирівнюванням (C++17)
void operator delete(void* ptr, std::size_t size, std::align_val_t al) noexcept;
void operator delete[](void* ptr, std::size_t size, std::align_val_t al) noexcept;
