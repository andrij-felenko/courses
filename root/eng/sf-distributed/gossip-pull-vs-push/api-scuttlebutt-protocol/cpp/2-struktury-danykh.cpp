#include <cstdint>
#include <vector>
#include <span>
#include <string_view>

inline constexpr uint16_t ScuttlebuttMagic = 0x5343;
inline constexpr uint8_t  ScuttlebuttProtoVer = 0x01;
inline constexpr size_t   ScuttlebuttMaxMtu = 1400;

/* Запис дайджесту версій вузла */
struct DigestEntry {
    uint32_t endpoint_id{0}; /* Унікальний ID цільового сервера */
    uint64_t generation{0};  /* Епоха/мітка старту процесу (Unix epoch мс) */
    uint64_t max_version{0}; /* Монотонний лічильник локальних змін стану */

    auto operator<=>(const DigestEntry&) const = default;
};

/* Запис дельти стану (конкретна мутація атрибута) */
struct DeltaEntry {
    uint32_t endpoint_id{0}; /* ID сервера-власника стану */
    uint16_t key_id{0};      /* Ідентифікатор ключа (Status, Tokens, Schema) */
    uint64_t generation{0};  /* Епоха власника стану */
    uint64_t version{0};     /* Точний порядковий номер версії */
    std::vector<uint8_t> value{}; /* Байти значення */
};
