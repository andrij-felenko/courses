#include <new>

// 1. Для одиничного об'єкта
void* operator new(std::size_t size, void* ptr) noexcept;

// 2. Для масиву об'єктів
void* operator new[](std::size_t size, void* ptr) noexcept;

// 3. Відповідні розміщувальні оператори delete
void operator delete(void* ptr, void* place) noexcept;
void operator delete[](void* ptr, void* place) noexcept;
