#include <cstdint>
#include <string_view>
#include <optional>
#include <span>

struct FlashGeometry {
    uint8_t          manufacturer_id{0};
    uint8_t          memory_type{0};
    uint8_t          capacity_id{0};
    uint32_t         total_size_bytes{0};
    uint32_t         sector_size_bytes{4096};
    uint32_t         page_size_bytes{256};
    uint32_t         total_sectors{0};
    std::string_view vendor_name{"Unknown"};
};

class JedecFlashIdentifier {
public:
    static constexpr uint8_t CmdReadId = 0x9F;

    [[nodiscard]] static constexpr std::string_view resolve_vendor(uint8_t mfg_id) noexcept {
        switch (mfg_id) {
            case 0xEF: return "Winbond";
            case 0xC2: return "Macronix";
            case 0xC8: return "GigaDevice";
            case 0x20: return "Micron/Numonyx";
            case 0x01: return "Spansion/Infineon";
            case 0xBF: return "Microchip/SST";
            case 0x9D: return "ISSI";
            case 0x85: return "Puya";
            case 0x68: return "Boya";
            case 0x5E: return "Zbit";
            default:   return "Unknown Vendor";
        }
    }

    [[nodiscard]] static constexpr std::optional<FlashGeometry> decode(std::span<const uint8_t, 3> raw_id) noexcept {
        const uint8_t mfg  = raw_id[0];
        const uint8_t type = raw_id[1];
        const uint8_t cap  = raw_id[2];

        // Захист від аварійних станів шини
        if ((mfg == 0xFF && type == 0xFF && cap == 0xFF) ||
            (mfg == 0x00 && type == 0x00 && cap == 0x00)) {
            return std::nullopt;
        }

        // Обмеження валідних показників ємності (від 2^16 = 64 КБ до 2^26 = 64 МБ)
        if (cap < 0x10 || cap > 0x1A) {
            return std::nullopt;
        }

        FlashGeometry geom;
        geom.manufacturer_id   = mfg;
        geom.memory_type       = type;
        geom.capacity_id       = cap;
        geom.total_size_bytes  = (1UL << cap);
        geom.sector_size_bytes = 4096;
        geom.page_size_bytes   = 256;
        geom.total_sectors     = geom.total_size_bytes / geom.sector_size_bytes;
        geom.vendor_name       = resolve_vendor(mfg);

        return geom;
    }
};
