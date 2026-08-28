#include <cstdint>
#include <span>

namespace fc::usb::dfu {

struct [[gnu::packed]] DfuFunctionalDescriptor {
    std::uint8_t  length{sizeof(DfuFunctionalDescriptor)};
    std::uint8_t  descriptor_type{0x21U}; // DFU Functional
    std::uint8_t  attributes{0x0BU};      // CanDnload | CanUpload | WillDetach
    std::uint16_t detach_timeout_ms{250U};
    std::uint16_t transfer_size_bytes{1024U};
    std::uint16_t bcd_dfu_version{0x0110U}; // DFU 1.1
};

inline constexpr DfuFunctionalDescriptor default_dfu_descriptor{};

enum class DfuState : std::uint8_t {
    AppIdle          = 0x00,
    AppDetach        = 0x01,
    DfuIdle          = 0x02,
    DfuDnloadSync    = 0x03,
    DfuDnBusy        = 0x04,
    DfuDnloadIdle    = 0x05,
    DfuManifestSync  = 0x06,
    DfuManifest      = 0x07,
    DfuError         = 0x0A
};

enum class DfuStatus : std::uint8_t {
    Ok               = 0x00,
    ErrTarget        = 0x01,
    ErrFile          = 0x02,
    ErrWrite         = 0x03,
    ErrErase         = 0x04,
    ErrCheckErased   = 0x05,
    ErrProg          = 0x06,
    ErrVerify        = 0x07,
    ErrAddress       = 0x08,
    ErrNotDone       = 0x09,
    ErrFirmware      = 0x0A,
    ErrVendor        = 0x0B,
    ErrUsbr          = 0x0C,
    ErrPor           = 0x0D,
    ErrUnknown       = 0x0E,
    ErrStalleP       = 0x0F
};

struct [[gnu::packed]] DfuStatusResponse {
    DfuStatus   status{DfuStatus::Ok};
    std::uint8_t poll_timeout[3]{0x05, 0x00, 0x00}; // 5 мс у 24-бітному Little-Endian
    DfuState    state{DfuState::DfuIdle};
    std::uint8_t string_index{0};
};

} // namespace fc::usb::dfu
