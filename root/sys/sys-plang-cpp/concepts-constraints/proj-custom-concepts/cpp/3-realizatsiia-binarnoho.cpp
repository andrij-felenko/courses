// Реалізація бінарного потоку пам'яті з підтримкою читання та запису
class MemoryBufferStream {
public:
    std::size_t write(std::span<const std::byte> bytes) {
        if (bytes.empty()) {
            return 0;
        }
        const auto prev_size = buffer_.size();
        buffer_.resize(prev_size + bytes.size());
        std::memcpy(buffer_.data() + prev_size, bytes.data(), bytes.size());
        return bytes.size();
    }

    std::size_t read(std::span<std::byte> dest) {
        if (dest.empty() || read_pos_ >= buffer_.size()) {
            return 0;
        }
        const auto available = buffer_.size() - read_pos_;
        const auto to_read = std::min(dest.size(), available);
        std::memcpy(dest.data(), buffer_.data() + read_pos_, to_read);
        read_pos_ += to_read;
        return to_read;
    }

    [[nodiscard]] std::span<const std::byte> data() const noexcept {
        return buffer_;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return buffer_.size();
    }

    [[nodiscard]] std::size_t remaining() const noexcept {
        return (read_pos_ < buffer_.size()) ? (buffer_.size() - read_pos_) : 0;
    }

    void reset_read() noexcept {
        read_pos_ = 0;
    }

    void clear() noexcept {
        buffer_.clear();
        read_pos_ = 0;
    }

private:
    std::vector<std::byte> buffer_;
    std::size_t read_pos_ = 0;
};

// Статична перевірка відповідності контрактів потоку
static_assert(ByteStream<MemoryBufferStream>);
static_assert(ByteSource<MemoryBufferStream>);
