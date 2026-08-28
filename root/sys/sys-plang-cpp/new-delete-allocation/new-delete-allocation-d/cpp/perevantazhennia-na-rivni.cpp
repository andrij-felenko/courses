class PacketNode {
public:
    explicit PacketNode(int priority) : priority_level(priority) {}

    // Статичні методи виділення пам'яті для конкретного класу
    static void* operator new(std::size_t size) {
        return PoolAllocator::allocate(size);
    }

    static void operator delete(void* ptr, std::size_t size) noexcept {
        PoolAllocator::deallocate(ptr, size);
    }

    // Класові версії для масивів
    static void* operator new[](std::size_t size) {
        return ::operator new(size); // Масиви відправляємо у стандартну купу
    }

    static void operator delete[](void* ptr) noexcept {
        ::operator delete(ptr);
    }

private:
    int priority_level;
};
