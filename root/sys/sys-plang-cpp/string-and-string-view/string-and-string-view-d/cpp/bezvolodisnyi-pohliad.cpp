// Концептуальний устрій std::string_view (sizeof = 16 байтів на 64-бітній системі)
class string_view {
    const char* ptr_ = nullptr;
    std::size_t size_ = 0;
public:
    constexpr string_view(const char* data, std::size_t len) 
        : ptr_(data), size_(len) {}
    
    constexpr const char* data() const noexcept { return ptr_; }
    constexpr std::size_t size() const noexcept { return size_; }
};
