#include <iostream>
#include <cstdint>
#include <bit>
#include <cmath>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <optional>
#include <variant>

enum class TypeKind : uint8_t {
    Double,
    Int32,
    Bool,
    Pointer,
    Null
};

class NanBoxedValue {
private:
    static constexpr uint64_t QNAN_MASK     = 0x7FF8'0000'0000'0000ULL;
    static constexpr uint64_t TAG_MASK      = 0x0007'0000'0000'0000ULL;
    static constexpr uint64_t PAYLOAD_MASK  = 0x0000'FFFF'FFFF'FFFFULL;

    static constexpr uint64_t TAG_POINTER   = 0x0001'0000'0000'0000ULL;
    static constexpr uint64_t TAG_INT       = 0x0002'0000'0000'0000ULL;
    static constexpr uint64_t TAG_BOOL      = 0x0003'0000'0000'0000ULL;
    static constexpr uint64_t TAG_NULL      = 0x0004'0000'0000'0000ULL;
    static constexpr uint64_t CANONICAL_NAN = 0x7FF8'0000'0000'0000ULL;

    uint64_t raw_bits_{QNAN_MASK | TAG_NULL};

    explicit constexpr NanBoxedValue(uint64_t raw) noexcept : raw_bits_(raw) {}

public:
    constexpr NanBoxedValue() noexcept = default;

    static NanBoxedValue from_double(double v) noexcept {
        if (std::isnan(v)) {
            return NanBoxedValue(CANONICAL_NAN);
        }
        return NanBoxedValue(std::bit_cast<uint64_t>(v));
    }

    static constexpr NanBoxedValue from_int(int32_t v) noexcept {
        return NanBoxedValue(QNAN_MASK | TAG_INT | static_cast<uint64_t>(static_cast<uint32_t>(v)));
    }

    static constexpr NanBoxedValue from_bool(bool b) noexcept {
        return NanBoxedValue(QNAN_MASK | TAG_BOOL | (b ? 1ULL : 0ULL));
    }

    static NanBoxedValue from_ptr(const void* ptr) noexcept {
        auto addr = reinterpret_cast<uintptr_t>(ptr);
        return NanBoxedValue(QNAN_MASK | TAG_POINTER | (addr & PAYLOAD_MASK));
    }

    static constexpr NanBoxedValue make_null() noexcept {
        return NanBoxedValue(QNAN_MASK | TAG_NULL);
    }

    [[nodiscard]] constexpr TypeKind kind() const noexcept {
        if ((raw_bits_ & QNAN_MASK) != QNAN_MASK) return TypeKind::Double;
        switch (raw_bits_ & (QNAN_MASK | TAG_MASK)) {
            case QNAN_MASK | TAG_INT:     return TypeKind::Int32;
            case QNAN_MASK | TAG_BOOL:    return TypeKind::Bool;
            case QNAN_MASK | TAG_POINTER: return TypeKind::Pointer;
            default:                      return TypeKind::Null;
        }
    }

    [[nodiscard]] constexpr bool is_double() const noexcept { return kind() == TypeKind::Double; }
    [[nodiscard]] constexpr bool is_int() const noexcept    { return kind() == TypeKind::Int32; }
    [[nodiscard]] constexpr bool is_bool() const noexcept   { return kind() == TypeKind::Bool; }
    [[nodiscard]] constexpr bool is_ptr() const noexcept    { return kind() == TypeKind::Pointer; }
    [[nodiscard]] constexpr bool is_null() const noexcept   { return kind() == TypeKind::Null; }

    [[nodiscard]] double as_double() const noexcept {
        return std::bit_cast<double>(raw_bits_);
    }

    [[nodiscard]] constexpr int32_t as_int() const noexcept {
        return static_cast<int32_t>(static_cast<uint32_t>(raw_bits_ & 0xFFFF'FFFFULL));
    }

    [[nodiscard]] constexpr bool as_bool() const noexcept {
        return (raw_bits_ & 1ULL) != 0;
    }

    [[nodiscard]] void* as_ptr() const noexcept {
        return reinterpret_cast<void*>(static_cast<uintptr_t>(raw_bits_ & PAYLOAD_MASK));
    }
};

/* Динамічна арифметика з ідіоматичним std::expected для обробки помилок */
struct TypeError {
    std::string message;
};

std::expected<NanBoxedValue, TypeError> add_dynamic(NanBoxedValue a, NanBoxedValue b) {
    if (a.is_int() && b.is_int()) {
        return NanBoxedValue::from_int(a.as_int() + b.as_int());
    }

    if ((a.is_double() || a.is_int()) && (b.is_double() || b.is_int())) {
        double da = a.is_double() ? a.as_double() : static_cast<double>(a.as_int());
        double db = b.is_double() ? b.as_double() : static_cast<double>(b.as_int());
        return NanBoxedValue::from_double(da + db);
    }

    return std::unexpected(TypeError{"TypeError: неможливо виконати операцію над несумісними типами"});
}

int main() {
    auto v1 = NanBoxedValue::from_int(40);
    auto v2 = NanBoxedValue::from_int(2);
    auto v3 = NanBoxedValue::from_double(3.14159);
    auto v_null = NanBoxedValue::make_null();

    if (auto res = add_dynamic(v1, v2); res) {
        std::cout << "Int + Int = " << res->as_int() << '\n';
    }

    if (auto res = add_dynamic(v1, v3); res) {
        std::cout << "Int + Double = " << res->as_double() << '\n';
    }

    if (auto res = add_dynamic(v1, v_null); !res) {
        std::cout << res.error().message << '\n';
    }

    std::cout << "Розмір NanBoxedValue: " << sizeof(NanBoxedValue) << " байтів\n";
    std::cout << "Розмір std::variant<double, int, bool, void*>: " 
              << sizeof(std::variant<double, int32_t, bool, void*>) << " байтів\n";
    return 0;
}
