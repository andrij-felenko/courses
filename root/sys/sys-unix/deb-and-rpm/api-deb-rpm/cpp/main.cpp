#include <cstdint>
#include <array>

struct RpmLead {
    std::array<uint8_t, 4> magic; /* 0xED, 0xAB, 0xEE, 0xDB */
    uint8_t major;                /* Версія формату (3 або 4) */
    uint8_t minor;                /* Підверсія формату */
    uint16_t type;                /* 0 = Binary, 1 = Source */
    uint16_t archtag;             /* Ідентифікатор архітектури */
    std::array<char, 66> name;    /* Назва пакунка */
    uint16_t osnum;               /* Ідентифікатор ОС */
    uint16_t signature_type;      /* Тип підпису */
    std::array<char, 16> reserved;/* Зарезервовано */
};
