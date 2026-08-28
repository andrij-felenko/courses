class SlotPool {
    std::array<Frame, 64> frames_{};
    std::bitset<64>       busy_{};
public:
    int    acquire() noexcept;                       // -1, якщо вільних немає
    void   give_back(int i) noexcept { busy_.reset(i); }
    Frame& frame(int i) noexcept { return frames_[i]; }
};

class SlotHandle {                                   // те саме, що FdHandle, про індекс
    int i_ = -1;
public:
    SlotHandle() = default;
    SlotHandle(std::nullptr_t) noexcept {}
    explicit SlotHandle(int i) noexcept : i_(i) {}
    int index() const noexcept { return i_; }
    friend bool operator==(SlotHandle a, SlotHandle b) noexcept { return a.i_ == b.i_; }
    friend bool operator==(SlotHandle h, std::nullptr_t) noexcept { return h.i_ == -1; }
};

class SlotReturn {
    SlotPool* pool_ = nullptr;                       // ← стан: куди повертати
public:
    using pointer = SlotHandle;
    SlotReturn() = default;
    explicit SlotReturn(SlotPool& p) noexcept : pool_(&p) {}
    void operator()(SlotHandle h) const noexcept { pool_->give_back(h.index()); }
};

using UniqueSlot = std::unique_ptr<Frame, SlotReturn>;

UniqueSlot take(SlotPool& pool) {
    return UniqueSlot(SlotHandle{pool.acquire()}, SlotReturn{pool});
}
