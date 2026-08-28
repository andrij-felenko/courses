#ifdef EXPERIMENT_NO_NOEXCEPT          // -DEXPERIMENT_NO_NOEXCEPT для другого прогону
#  define MOVE_NOEXCEPT
#else
#  define MOVE_NOEXCEPT noexcept
#endif

class Buffer {
    std::byte*  data_ = nullptr;
    std::size_t size_ = 0;

public:
    explicit Buffer(std::size_t n)
        : data_(n ? new std::byte[n] : nullptr), size_(n) {
        ++g.ctor;
    }

    ~Buffer() {                                            // 1. деструктор
        ++g.dtor;
        delete[] data_;                                    // на nullptr — законний нуль-ефект
    }

    Buffer(const Buffer& other)                            // 2. копіювання
        : data_(other.size_ ? new std::byte[other.size_] : nullptr),
          size_(other.size_) {
        if (size_) std::memcpy(data_, other.data_, size_);
        ++g.copy_ctor;
        g.bytes_copied += size_;
    }

    Buffer& operator=(const Buffer& other) {               // 3. копіювальне присвоєння
        std::byte* fresh = other.size_ ? new std::byte[other.size_] : nullptr;
        if (other.size_) std::memcpy(fresh, other.data_, other.size_);
        delete[] data_;                     // своє звільняємо ПІСЛЯ вдалого виділення
        data_ = fresh;
        size_ = other.size_;
        ++g.copy_assign;
        g.bytes_copied += size_;
        return *this;
    }

    Buffer(Buffer&& other) MOVE_NOEXCEPT                   // 4. переміщення
        : data_(std::exchange(other.data_, nullptr)),
          size_(std::exchange(other.size_, 0)) {
        ++g.move_ctor;
    }

    Buffer& operator=(Buffer&& other) noexcept {           // 5. переміщувальне присвоєння
        if (this == &other) return *this;   // без цього рядка — звільнений вказівник
        delete[] data_;
        data_ = std::exchange(other.data_, nullptr);
        size_ = std::exchange(other.size_, 0);
        ++g.move_assign;
        return *this;
    }

    void swap(Buffer& other) noexcept {
        std::swap(data_, other.data_);
        std::swap(size_, other.size_);
    }

    std::size_t size() const noexcept { return size_; }
};

#ifndef EXPERIMENT_NO_NOEXCEPT
static_assert(std::is_nothrow_move_constructible_v<Buffer>,
              "тип із ресурсом мусить переміщуватися без винятків");
#endif
