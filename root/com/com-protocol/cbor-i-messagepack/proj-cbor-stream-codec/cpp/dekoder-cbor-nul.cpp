class Decoder {
public:
    static std::expected<Value, Error> read_next(Reader& r) noexcept {
        if (r.remaining() == 0) {
            return std::unexpected(Error::UnexpectedEof);
        }

        const uint8_t initial_byte = r.buf_[r.offset_++];
        const auto major = static_cast<MajorType>(initial_byte >> 5);
        const uint8_t info = initial_byte & 0x1F;

        auto uint_res = read_uint_payload(r, info);
        if (!uint_res) {
            return std::unexpected(uint_res.error());
        }
        const uint64_t val = *uint_res;

        switch (major) {
            case MajorType::UnsignedInt:
                return val;

            case MajorType::NegativeInt:
                return static_cast<int64_t>(-1 - static_cast<int64_t>(val));

            case MajorType::ByteString: {
                if (r.remaining() < val) return std::unexpected(Error::UnexpectedEof);
                auto slice = r.buf_.subspan(r.offset_, val);
                r.offset_ += val;
                return slice;
            }

            case MajorType::TextString: {
                if (r.remaining() < val) return std::unexpected(Error::UnexpectedEof);
                std::string_view sv(reinterpret_cast<const char*>(r.buf_.data() + r.offset_), val);
                r.offset_ += val;
                return sv;
            }

            case MajorType::Array:
                return ArrayHeader{static_cast<size_t>(val)};

            case MajorType::Map:
                return MapHeader{static_cast<size_t>(val)};

            case MajorType::Tag:
                return TagHeader{val};

            case MajorType::Simple:
                if (info == 20) return false;
                if (info == 21) return true;
                if (info == 22) return NullValue{};
                if (info == 26) {
                    uint32_t raw = static_cast<uint32_t>(val);
                    float f;
                    std::memcpy(&f, &raw, sizeof(float));
                    return f;
                }
                return std::unexpected(Error::UnsupportedType);
        }
        return std::unexpected(Error::UnsupportedType);
    }

private:
    static std::expected<uint64_t, Error> read_uint_payload(Reader& r, uint8_t info) noexcept {
        if (info < 24) return info;
        if (info == 24) {
            if (r.remaining() < 1) return std::unexpected(Error::UnexpectedEof);
            return r.buf_[r.offset_++];
        }
        if (info == 25) {
            if (r.remaining() < 2) return std::unexpected(Error::UnexpectedEof);
            uint64_t v = (static_cast<uint64_t>(r.buf_[r.offset_]) << 8) |
                          static_cast<uint64_t>(r.buf_[r.offset_ + 1]);
            r.offset_ += 2;
            return v;
        }
        if (info == 26) {
            if (r.remaining() < 4) return std::unexpected(Error::UnexpectedEof);
            uint64_t v = (static_cast<uint64_t>(r.buf_[r.offset_]) << 24) |
                         (static_cast<uint64_t>(r.buf_[r.offset_ + 1]) << 16) |
                         (static_cast<uint64_t>(r.buf_[r.offset_ + 2]) << 8) |
                          static_cast<uint64_t>(r.buf_[r.offset_ + 3]);
            r.offset_ += 4;
            return v;
        }
        if (info == 27) {
            if (r.remaining() < 8) return std::unexpected(Error::UnexpectedEof);
            uint64_t v = 0;
            for (size_t i = 0; i < 8; ++i) {
                v = (v << 8) | static_cast<uint64_t>(r.buf_[r.offset_ + i]);
            }
            r.offset_ += 8;
            return v;
        }
        return std::unexpected(Error::InvalidHeader);
    }
};
