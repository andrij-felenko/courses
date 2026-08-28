// Strong-typed enum class у C++20 для безпечної роботи з атрибутами Netlink
#include <cstdint>

enum class MacsecSaAttr : std::uint16_t {
    Unspec = 0,
    AssociationNumber, // MACSEC_SA_ATTR_AN (u8: 0..3)
    Active,            // MACSEC_SA_ATTR_ACTIVE (u8: 0 або 1)
    PacketNumber,      // MACSEC_SA_ATTR_PN (u32/u64)
    KeyId,             // MACSEC_SA_ATTR_KEYID (16B)
    KeyMaterial,       // MACSEC_SA_ATTR_KEY (16B/32B)
    Stats              // MACSEC_SA_ATTR_STATS
};
