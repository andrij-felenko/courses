class FixedPool {
private:
    struct FreeNode {
        FreeNode* next;
    };

public:
    FixedPool(std::size_t block_size, std::size_t block_count, std::size_t alignment)
        : block_size_(std::max(block_size, sizeof(FreeNode))),
          block_count_(block_count),
          alignment_(std::max(alignment, alignof(FreeNode))),
          free_list_(nullptr) {
        stride_ = (block_size_ + alignment_ - 1) & ~(alignment_ - 1);
        buffer_ = static_cast<std::byte*>(::operator new(stride_ * block_count_, std::align_val_t{alignment_}));
        reset();
    }

    ~FixedPool() {
        ::operator delete(buffer_, std::align_val_t{alignment_});
    }

    FixedPool(const FixedPool&) = delete;
    FixedPool& operator=(const FixedPool&) = delete;

    [[nodiscard]] void* allocate() {
        if (!free_list_) {
            throw std::bad_alloc();
        }
        FreeNode* node = free_list_;
        free_list_ = free_list_->next;
        allocated_count_++;
        return static_cast<void*>(node);
    }

    void deallocate(void* p) noexcept {
        if (!p) return;
        FreeNode* node = static_cast<FreeNode*>(p);
        node->next = free_list_;
        free_list_ = node;
        allocated_count_--;
    }

    void reset() noexcept {
        free_list_ = nullptr;
        allocated_count_ = 0;
        for (std::size_t i = 0; i < block_count_; ++i) {
            FreeNode* node = reinterpret_cast<FreeNode*>(buffer_ + i * stride_);
            node->next = free_list_;
            free_list_ = node;
        }
    }

    [[nodiscard]] std::size_t allocated_count() const noexcept { return allocated_count_; }
    [[nodiscard]] std::size_t block_count() const noexcept { return block_count_; }

private:
    std::size_t block_size_;
    std::size_t block_count_;
    std::size_t alignment_;
    std::size_t stride_;
    std::byte* buffer_;
    FreeNode* free_list_;
    std::size_t allocated_count_ = 0;
};
