class Encoder {
public:
    static std::expected<void, Error> write_uint(Writer& w, uint64_t val) noexcept {
        return write_header(w, MajorType::UnsignedInt, val);
    }

    static std::expected<void, Error> write_int(Writer& w, int64_t val) noexcept {
        if (val >= 0) {
            return write_uint(w, static_cast<uint64_t>(val));
        }
        uint64_t encoded = static_cast<uint64_t>(-1 - val);
        return write_header(w, MajorType::NegativeInt, encoded);
    }

    static std::expected<void, Error> write_text(Writer& w, std::string_view sv) noexcept {
        auto res = write_header(w, MajorType::TextString, sv.size());
        if (!res) return res;
        if (w.remaining_capacity() < sv.size()) return std::unexpected(Error::BufferOverflow);
        std::memcpy(w.buf_.data() + w.offset_, sv.data(), sv.size());
        w.offset_ += sv.size();
        return {};
    }

    static std::expected<void, Error> write_bytes(Writer& w, std::span<const uint8_t> bytes) noexcept {
        auto res = write_header(w, MajorType::ByteString, bytes.size());
        if (!res) return res;
        if (w.remaining_capacity() < bytes.size()) return std::unexpected(Error::BufferOverflow);
        std::memcpy(w.buf_.data() + w.offset_, bytes.data(), bytes.size());
        w.offset_ += bytes.size();
        return {};
    }

    static std::expected<void, Error> write_map_header(Writer& w, size_t num_pairs) noexcept {
        return write_header(w, MajorType::Map, num_pairs);
    }

    static std::expected<void, Error> write_array_header(Writer& w, size_t num_items) noexcept {
        return write_header(w, MajorType::Array, num_items);
    }

    static std::expected<void, Error> write_bool(Writer& w, bool val) noexcept {
        if (w.remaining_capacity() < 1) return std::unexpected(Error::BufferOverflow);
        uint8_t byte = (static_cast<uint8_t>(MajorType::Simple) << 5) | (val ? 21 : 20);
        w.buf_[w.offset_++] = byte;
        return {};
    }

private:
    static std::expected<void, Error> write_header(Writer& w, MajorType major, uint64_t val) noexcept {
        const uint8_t major_bits = static_cast<uint8_t>(major) << 5;
        if (val < 24) {
            if (w.remaining_capacity() < 1) return std::unexpected(Error::BufferOverflow);
            w.buf_[w.offset_++] = major_bits | static_cast<uint8_t>(val);
            return {};
        }
        if (val <= 0xFF) {
            if (w.remaining_capacity() < 2) return std::unexpected(Error::BufferOverflow);
            w.buf_[w.offset_++] = major_bits | 24;
            w.buf_[w.offset_++] = static_cast<uint8_t>(val);
            return {};
        }
        if (val <= 0xFFFF) {
            if (w.remaining_capacity() < 3) return std::unexpected(Error::BufferOverflow);
            w.buf_[w.offset_++] = major_bits | 25;
            w.buf_[w.offset_++] = static_cast<uint8_t>(val >> 8);
            w.buf_[w.offset_++] = static_cast<uint8_t>(val & 0xFF);
            return {};
        }
        if (val <= 0xFFFFFFFF) {
            if (w.remaining_capacity() < 5) return std::unexpected(Error::BufferOverflow);
            w.buf_[w.offset_++] = major_bits | 26;
            for (int i = 3; i >= 0; --i) {
                w.buf_[w.offset_++] = static_cast<uint8_t>((val >> (i * 8)) & 0xFF);
            }
            return {};
        }
        if (w.remaining_capacity() < 9) return std::unexpected(Error::BufferOverflow);
        w.buf_[w.offset_++] = major_bits | 27;
        for (int i = 7; i >= 0; --i) {
            w.buf_[w.offset_++] = static_cast<uint8_t>((val >> (i * 8)) & 0xFF);
        }
        return {};
    }
};
