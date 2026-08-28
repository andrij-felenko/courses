#include <cstdint>
#include <bit>
#include <span>
#include <array>

#pragma pack(push, 1)

/* Типізований селектор сегмента x86 у стандарті C++20 */
struct SegmentSelector {
    uint16_t raw{0};

    [[nodiscard]] constexpr uint8_t rpl() const noexcept {
        return static_cast<uint8_t>(raw & 0x03);
    }

    [[nodiscard]] constexpr bool is_ldt() const noexcept {
        return (raw & 0x04) != 0;
    }

    [[nodiscard]] constexpr uint16_t index() const noexcept {
        return raw >> 3;
    }

    static constexpr SegmentSelector from_parts(uint16_t idx, bool ldt, uint8_t priv_level) noexcept {
        return SegmentSelector{
            static_cast<uint16_t>((idx << 3) | (ldt ? 0x04 : 0x00) | (priv_level & 0x03))
        };
    }
};

/* Дескриптор сегмента IA-32 */
struct SegmentDescriptor {
    uint16_t limit_low{0};
    uint16_t base_low{0};
    uint8_t  base_mid{0};
    uint8_t  type : 4 {0};
    uint8_t  s : 1 {1};
    uint8_t  dpl : 2 {0};
    uint8_t  present : 1 {1};
    uint8_t  limit_high : 4 {0};
    uint8_t  avl : 1 {0};
    uint8_t  long_mode : 1 {0};
    uint8_t  db_size : 1 {1};
    uint8_t  granularity : 1 {1};
    uint8_t  base_high{0};

    [[nodiscard]] constexpr uint32_t base() const noexcept {
        return (static_cast<uint32_t>(base_high) << 24) |
               (static_cast<uint32_t>(base_mid)  << 16) |
               (static_cast<uint32_t>(base_low));
    }

    [[nodiscard]] constexpr uint32_t limit_in_bytes() const noexcept {
        const uint32_t lim = (static_cast<uint32_t>(limit_high) << 16) | limit_low;
        return granularity ? ((lim << 12) | 0xFFF) : lim;
    }

    /* Фабрика плоского сегмента (Flat Model 4 GB) */
    static constexpr SegmentDescriptor make_flat(uint8_t seg_type, uint8_t priv_dpl, bool code_64) noexcept {
        SegmentDescriptor desc{};
        desc.base_low = 0;
        desc.base_mid = 0;
        desc.base_high = 0;
        desc.limit_low = 0xFFFF;
        desc.limit_high = 0x0F;
        desc.type = seg_type;
        desc.s = 1;
        desc.dpl = priv_dpl;
        desc.present = 1;
        desc.granularity = 1; /* Множення на 4 КБ -> 4 ГБ */
        desc.db_size = code_64 ? 0 : 1;
        desc.long_mode = code_64 ? 1 : 0;
        return desc;
    }
};

/* 80-бітний псевдодескриптор GDTR у 64-бітному режимі */
struct alignas(2) Gdtr64 {
    uint16_t limit{0};
    uint64_t base_address{0};

    explicit constexpr Gdtr64(std::span<const SegmentDescriptor> gdt_view) noexcept
        : limit(static_cast<uint16_t>(gdt_view.size_bytes() - 1)),
          base_address(reinterpret_cast<uint64_t>(gdt_view.data())) {}

    void install() const noexcept {
        asm volatile("lgdt %0" : : "m"(*this) : "memory");
    }
};

#pragma pack(pop)
