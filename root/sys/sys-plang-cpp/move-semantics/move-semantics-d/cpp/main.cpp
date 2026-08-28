class Buffer {
    std::byte*  data_ = nullptr;
    std::size_t size_ = 0;

public:
    explicit Buffer(std::size_t n)
        : data_(new std::byte[n]), size_(n) {}

    ~Buffer() { delete[] data_; }

    Buffer(const Buffer& other)                       // копіювання
        : data_(new std::byte[other.size_]), size_(other.size_) {
        std::memcpy(data_, other.data_, size_);
    }

    Buffer(Buffer&& other) noexcept                   // переміщення
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }
};
