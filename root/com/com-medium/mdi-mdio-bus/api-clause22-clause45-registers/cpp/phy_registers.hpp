// phy_registers.hpp - Сучасний C++20 інтерфейс типів та констант регістрів PHY
#pragma once

#include <cstdint>
#include <string_view>

namespace eth::phy {

enum class Clause22Reg : uint8_t {
    Bmcr        = 0x00,
    Bmsr        = 0x01,
    PhyId1      = 0x02,
    PhyId2      = 0x03,
    Anar        = 0x04,
    Anlpar      = 0x05,
    Aner        = 0x06,
    GbeControl  = 0x09,
    GbeStatus   = 0x0A,
    MmdCtrl     = 0x0D,
    MmdData     = 0x0E,
    ExtStatus   = 0x0F,
};

namespace bmcr {
    inline constexpr uint16_t Reset        = 1U << 15;
    inline constexpr uint16_t Loopback     = 1U << 14;
    inline constexpr uint16_t Speed100     = 1U << 13;
    inline constexpr uint16_t AutoNegEn    = 1U << 12;
    inline constexpr uint16_t PowerDown    = 1U << 11;
    inline constexpr uint16_t Isolate      = 1U << 10;
    inline constexpr uint16_t RestartAn    = 1U << 9;
    inline constexpr uint16_t FullDuplex   = 1U << 8;
    inline constexpr uint16_t ColTest      = 1U << 7;
    inline constexpr uint16_t Speed1000    = 1U << 6;
}

namespace bmsr {
    inline constexpr uint16_t Speed100T4   = 1U << 15;
    inline constexpr uint16_t Speed100Fd   = 1U << 14;
    inline constexpr uint16_t Speed100Hd   = 1U << 13;
    inline constexpr uint16_t Speed10Fd    = 1U << 12;
    inline constexpr uint16_t Speed10Hd    = 1U << 11;
    inline constexpr uint16_t PreSuppr     = 1U << 6;
    inline constexpr uint16_t AnComplete   = 1U << 5;
    inline constexpr uint16_t RemoteFault  = 1U << 4;
    inline constexpr uint16_t AnAbility    = 1U << 3;
    inline constexpr uint16_t LinkStatus   = 1U << 2;
    inline constexpr uint16_t Jabber       = 1U << 1;
    inline constexpr uint16_t ExtCap       = 1U << 0;
}

namespace gbe_ctrl {
    inline constexpr uint16_t ManualMaster = 1U << 12;
    inline constexpr uint16_t MasterVal    = 1U << 11;
    inline constexpr uint16_t MultiPort    = 1U << 10;
    inline constexpr uint16_t Adv1000Fd    = 1U << 9;
    inline constexpr uint16_t Adv1000Hd    = 1U << 8;
}

enum class MmdDevice : uint8_t {
    PmdPma   = 1,
    Wis      = 2,
    Pcs      = 3,
    PhyXs    = 4,
    DteXs    = 5,
    AutoNeg  = 7,
    Vendor1  = 29,
    Vendor2  = 30,
};

struct PhyIdentifier {
    uint32_t oui;
    uint8_t  model;
    uint8_t  revision;

    [[nodiscard]] static constexpr PhyIdentifier from_registers(uint16_t id1, uint16_t id2) noexcept {
        const uint32_t oui_raw = (static_cast<uint32_t>(id1) << 6) | ((id2 >> 10) & 0x3FU);
        const uint8_t  model   = static_cast<uint8_t>((id2 >> 4) & 0x3FU);
        const uint8_t  rev     = static_cast<uint8_t>(id2 & 0x0FU);
        return { oui_raw, model, rev };
    }
};

} // namespace eth::phy
