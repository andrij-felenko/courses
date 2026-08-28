namespace physics::mechanics {

class MemoryArena {
public:
    MemoryArena(std::span<std::byte> buffer) : buffer_(buffer) {}
private:
    std::span<std::byte> buffer_;
};

}
