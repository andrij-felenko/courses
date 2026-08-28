namespace msm {

/* Арена-алокатор для керування пам'яттю кошиків */
class MemoryArena {
public:
    explicit MemoryArena(size_t capacity)
        : capacity_(capacity), offset_(0), buffer_(std::make_unique<uint8_t[]>(capacity)) {}

    void* allocate(size_t size, size_t alignment = alignof(std::max_align_t)) {
        const size_t aligned = (offset_ + (alignment - 1)) & ~(alignment - 1);
        if (aligned + size > capacity_) {
            return nullptr;
        }
        void* ptr = &buffer_[aligned];
        offset_ = aligned + size;
        return ptr;
    }

    void reset() noexcept {
        offset_ = 0;
    }

private:
    size_t capacity_;
    size_t offset_;
    std::unique_ptr<uint8_t[]> buffer_;
};

} // namespace msm
