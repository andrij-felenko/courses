#include <string_view>
#include <vector>
#include <cstddef>
#include <cstdint>

namespace vmstate {

struct SerialState {
    uint16_t divider{0};
    uint8_t  rbr{0};
    uint8_t  ier{0};
    uint8_t  iir{0};
    uint8_t  lcr{0};
    uint8_t  mcr{0};
    uint8_t  lsr{0};
    uint8_t  msr{0};
    uint8_t  scr{0};
};

struct FieldDescriptor {
    std::string_view name;
    size_t offset;
    size_t size;
};

struct DeviceStateDescription {
    std::string_view name;
    int version_id{1};
    int minimum_version_id{1};
    std::vector<FieldDescriptor> fields;
};

inline const DeviceStateDescription kSerialStateDesc{
    "serial",
    3,
    2,
    {
        { "divider", offsetof(SerialState, divider), sizeof(uint16_t) },
        { "rbr",     offsetof(SerialState, rbr),     sizeof(uint8_t) },
        { "ier",     offsetof(SerialState, ier),     sizeof(uint8_t) },
        { "iir",     offsetof(SerialState, iir),     sizeof(uint8_t) },
        { "lcr",     offsetof(SerialState, lcr),     sizeof(uint8_t) },
        { "mcr",     offsetof(SerialState, mcr),     sizeof(uint8_t) },
        { "lsr",     offsetof(SerialState, lsr),     sizeof(uint8_t) },
        { "msr",     offsetof(SerialState, msr),     sizeof(uint8_t) },
        { "scr",     offsetof(SerialState, scr),     sizeof(uint8_t) }
    }
};

} // namespace vmstate
