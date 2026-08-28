// param_pck.hpp — розбір @PARAM/param.pck (ArduPilot).
// C++17, без Qt, без винятків, без залежності від порядку байтів машини.
#include <cstdint>
#include <cstring>
#include <optional>
#include <string>
#include <variant>
#include <vector>

namespace pck {

enum class Err {
    ok, short_header, bad_magic, bad_counts, bad_type,
    name_overflow, truncated, missing_params, trailing_garbage
};

using Value = std::variant<int8_t, int16_t, int32_t, float>;

struct Param {
    std::string          name;
    Value                value;
    std::optional<Value> fw_default;   // порожнє ⇒ значення й є заводським
};

// ── читання little-endian явно: працює однаково на будь-якій машині ──────────
inline uint16_t le16(const uint8_t* b) {
    return uint16_t(uint16_t(b[0]) | (uint16_t(b[1]) << 8));
}
inline uint32_t le32(const uint8_t* b) {
    return uint32_t(b[0]) | (uint32_t(b[1]) << 8)
         | (uint32_t(b[2]) << 16) | (uint32_t(b[3]) << 24);
}

inline uint8_t type_size(uint8_t t) {
    switch (t) {
    case 1:  return 1;      // int8
    case 2:  return 2;      // int16
    case 3:  return 4;      // int32
    case 4:  return 4;      // float
    default: return 0;      // 0, 5, 6 у файлі не трапляються
    }
}

// звуження до знакового типу — модульне (гарантовано з C++20, на практиці всюди)
inline Value decode(uint8_t t, const uint8_t* b) {
    switch (t) {
    case 1:  return int8_t(b[0]);
    case 2:  return int16_t(le16(b));
    case 3:  return int32_t(le32(b));
    default: {
        static_assert(sizeof(float) == 4, "очікуємо 4-байтовий float IEEE-754");
        const uint32_t bits = le32(b);
        float f;
        std::memcpy(&f, &bits, sizeof f);   // саме копія бітів, не перетворення числа
        return f;
    }
    }
}

class Parser {
public:
    Parser(const uint8_t* data, size_t size) : p_(data), end_(data + size) {}

    Err run(std::vector<Param>& out) {
        if (size_t(end_ - p_) < 6) return Err::short_header;
        const uint16_t magic = le16(p_);
        const uint16_t num   = le16(p_ + 2);
        const uint16_t total = le16(p_ + 4);
        p_ += 6;
        if (magic != 0x671B && magic != 0x671C) return Err::bad_magic;
        if (num > total)                        return Err::bad_counts;

        out.clear();
        out.reserve(num);

        while (out.size() < size_t(num)) {
            // набивка: нуль не може починати запис, отже все нульове — сміття
            while (p_ != end_ && *p_ == 0) ++p_;
            if (p_ == end_)            return Err::missing_params;
            if (size_t(end_ - p_) < 2) return Err::truncated;

            const uint8_t b0 = p_[0];
            const uint8_t b1 = p_[1];
            p_ += 2;

            const uint8_t type   = b0 & 0x0F;
            const bool    hasdef = (b0 >> 4) & 0x01;
            const uint8_t common = b1 & 0x0F;
            const uint8_t nlen   = uint8_t(((b1 >> 4) & 0x0F) + 1);

            const uint8_t tlen = type_size(type);
            if (tlen == 0)               return Err::bad_type;
            if (common + nlen > 16)      return Err::name_overflow;
            if (common > last_.size())   return Err::name_overflow;  // спільного стільки нема

            const size_t need = size_t(nlen) + size_t(tlen) * (hasdef ? 2u : 1u);
            if (size_t(end_ - p_) < need) return Err::truncated;

            std::string name = last_.substr(0, common);
            name.append(reinterpret_cast<const char*>(p_), nlen);
            p_ += nlen;

            Param prm;
            prm.value = decode(type, p_);
            p_ += tlen;
            if (hasdef) {
                prm.fw_default = decode(type, p_);
                p_ += tlen;
            }
            last_     = name;                  // база стиснення для НАСТУПНОГО запису
            prm.name  = std::move(name);
            out.push_back(std::move(prm));
        }

        while (p_ != end_)                     // хвіст файлу — тільки набивка
            if (*p_++ != 0) return Err::trailing_garbage;
        return Err::ok;
    }

private:
    const uint8_t* p_;
    const uint8_t* end_;
    std::string    last_;                      // попереднє ім'я, до 16 байтів
};

inline double as_double(const Value& v) {
    return std::visit([](auto x) { return double(x); }, v);
}

} // namespace pck

// ── застосування ────────────────────────────────────────────────────────────
// std::vector<pck::Param> params;
// const pck::Err e = pck::Parser(blob.data(), blob.size()).run(params);
// if (e != pck::Err::ok) { /* файл побитий — звичайне завантаження потоком */ }
