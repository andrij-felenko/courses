namespace storage {
    class BigBuffer {
    private:
        uint8_t* ptr_ = nullptr;
        size_t size_ = 0;

    public:
        BigBuffer(size_t sz) : ptr_(new uint8_t[sz]), size_(sz) {}
        ~BigBuffer() { delete[] ptr_; }

        BigBuffer(const BigBuffer&) = delete;
        BigBuffer& operator=(const BigBuffer&) = delete;

        BigBuffer(BigBuffer&& o) noexcept : ptr_(o.ptr_), size_(o.size_) {
            o.ptr_ = nullptr;
            o.size_ = 0;
        }

        BigBuffer& operator=(BigBuffer&& o) noexcept {
            if (this != &o) {
                delete[] ptr_;
                ptr_ = o.ptr_;
                size_ = o.size_;
                o.ptr_ = nullptr;
                o.size_ = 0;
            }
            return *this;
        }

        // Дружня точка налаштування для ADL swap
        friend void swap(BigBuffer& a, BigBuffer& b) noexcept {
            using std::swap;
            swap(a.ptr_, b.ptr_);
            swap(a.size_, b.size_);
        }
    };
}
