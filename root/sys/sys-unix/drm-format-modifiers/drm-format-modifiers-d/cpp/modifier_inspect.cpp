// modifier_inspect.cpp — об'єктно-орієнтований інспектор модифікаторів C++20
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <string>
#include <string_view>
#include <drm_fourcc.h>

namespace drm {

class FormatModifier {
public:
    constexpr explicit FormatModifier(uint64_t mod = DRM_FORMAT_MOD_INVALID) noexcept
        : modifier_(mod) {}

    [[nodiscard]] constexpr uint64_t raw() const noexcept { return modifier_; }
    [[nodiscard]] constexpr uint8_t vendor_id() const noexcept {
        return static_cast<uint8_t>((modifier_ >> 56) & 0xff);
    }
    [[nodiscard]] constexpr uint64_t value() const noexcept {
        return modifier_ & 0x00ffffffffffffffULL;
    }

    [[nodiscard]] constexpr bool is_linear() const noexcept {
        return modifier_ == DRM_FORMAT_MOD_LINEAR;
    }
    [[nodiscard]] constexpr bool is_invalid() const noexcept {
        return modifier_ == DRM_FORMAT_MOD_INVALID;
    }

    [[nodiscard]] std::string_view vendor_name() const noexcept {
        switch (vendor_id()) {
            case DRM_FORMAT_MOD_VENDOR_NONE:     return "Generic (Standard)";
            case DRM_FORMAT_MOD_VENDOR_INTEL:    return "Intel";
            case DRM_FORMAT_MOD_VENDOR_AMD:      return "AMD";
            case DRM_FORMAT_MOD_VENDOR_NVIDIA:   return "NVIDIA";
            case DRM_FORMAT_MOD_VENDOR_SAMSUNG:  return "Samsung";
            case DRM_FORMAT_MOD_VENDOR_QCOM:     return "Qualcomm";
            case DRM_FORMAT_MOD_VENDOR_VIVANTE:  return "Vivante";
            case DRM_FORMAT_MOD_VENDOR_BROADCOM: return "Broadcom";
            case DRM_FORMAT_MOD_VENDOR_ARM:      return "Arm (AFBC)";
            case DRM_FORMAT_MOD_VENDOR_ALLWINNER:return "Allwinner";
            case DRM_FORMAT_MOD_VENDOR_AMLOGIC:  return "Amlogic";
            default:                             return "Unknown Vendor";
        }
    }

    void dump_info() const {
        if (is_invalid()) {
            std::cout << "Модифікатор: DRM_FORMAT_MOD_INVALID (Неявний вибір драйвером)\n";
            return;
        }
        if (is_linear()) {
            std::cout << "Модифікатор: DRM_FORMAT_MOD_LINEAR (Суцільний растровий порядок рядків, CPU-сумісний)\n";
            return;
        }

        std::cout << "Модифікатор: 0x" << std::hex << std::setw(16) << std::setfill('0')
                  << modifier_ << std::dec << "\n"
                  << "  Виробник: " << vendor_name()
                  << " (ID: 0x" << std::hex << static_cast<int>(vendor_id()) << std::dec << ")\n"
                  << "  Код розкладки: 0x" << std::hex << value() << std::dec << "\n";

        if (vendor_id() == DRM_FORMAT_MOD_VENDOR_INTEL) {
            if (modifier_ == I915_FORMAT_MOD_4_TILED_DG2_RC_CCS) {
                std::cout << "  Опис: Intel Tile4 з апаратним стисненням Render Compression (Arc DG2)\n";
            } else if (modifier_ == I915_FORMAT_MOD_4_TILED) {
                std::cout << "  Опис: Intel Tile4 нестиснений (DG2 / Meteor Lake)\n";
            } else if (modifier_ == I915_FORMAT_MOD_Y_TILED) {
                std::cout << "  Опис: Intel Y-Tiled (Класичний тайлінг 4 КБ Gen6-Gen11)\n";
            }
        } else if (vendor_id() == DRM_FORMAT_MOD_VENDOR_ARM) {
            std::cout << "  Опис: Arm FrameBuffer Compression (AFBC)\n";
            if (modifier_ & AFBC_FORMAT_MOD_YTR) {
                std::cout << "  Опція: YTR (Колірна трансформація простору)\n";
            }
        }
    }

private:
    uint64_t modifier_{DRM_FORMAT_MOD_INVALID};
};

} // namespace drm
