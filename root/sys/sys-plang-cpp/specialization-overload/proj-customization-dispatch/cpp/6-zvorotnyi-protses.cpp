class BinaryReader {
public:
    explicit BinaryReader(std::span<const uint8_t> data) 
        : buffer_(data), offset_(0) {}

    template<typename T>
    void read_raw(T& destination) {
        if (offset_ + sizeof(T) > buffer_.size()) {
            throw std::runtime_error("Недостатньо байтів у буфері для читання скаляра");
        }
        std::memcpy(&destination, buffer_.data() + offset_, sizeof(T));
        offset_ += sizeof(T);
    }

    void read_bytes(void* dest, std::size_t size) {
        if (offset_ + size > buffer_.size()) {
            throw std::runtime_error("Недостатньо байтів у буфері для читання масиву");
        }
        std::memcpy(dest, buffer_.data() + offset_, size);
        offset_ += size;
    }

    [[nodiscard]] bool empty() const noexcept {
        return offset_ >= buffer_.size();
    }

private:
    std::span<const uint8_t> buffer_;
    std::size_t offset_;
};

// Десеріалізація для моделі C++20
template<typename T>
T deserialize(BinaryReader& reader) {
    using PureType = std::remove_cvref_t<T>;

    if constexpr (std::same_as<PureType, std::string>) {
        uint32_t len = 0;
        reader.read_raw(len);
        std::string str(len, '\0');
        reader.read_bytes(str.data(), len);
        return str;
    } 
    else if constexpr (std::is_integral_v<PureType>) {
        PureType val{};
        reader.read_raw(val);
        if constexpr (sizeof(PureType) > 1 && std::endian::native == std::endian::little) {
            val = std::byteswap(val);
        }
        return val;
    } 
    else if constexpr (std::is_trivially_copyable_v<PureType>) {
        PureType val{};
        reader.read_raw(val);
        return val;
    } 
    else {
        static_assert(!sizeof(T), "Десеріалізація для цього типу не реалізована");
    }
}
