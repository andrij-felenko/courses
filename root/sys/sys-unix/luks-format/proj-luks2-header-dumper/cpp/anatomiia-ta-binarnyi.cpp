constexpr std::string_view LUKS2_MAGIC = "LUKS\xba\xbe";
constexpr std::size_t LUKS2_HDR_SIZE = 4096;

struct alignas(1) HeaderDisk {
    char     magic[6];        // 6 байтів: "LUKS\xba\xbe" або "SKUL\xba\xbe"
    uint16_t version;         // 2 байти: версія формату 0x0002
    uint64_t hdr_size;        // 8 байтів: повний розмір метаданих
    uint64_t seqid;           // 8 байтів: монотонний лічильник транзакцій
    char     label[48];       // 48 байтів: мітка тома
    char     csum_alg[32];    // 32 байти: алгоритм контрольної суми
    uint8_t  salt[64];        // 64 байти: криптографічна сіль
    char     uuid[44];        // 44 байти: унікальний UUID
    char     subsystem[48];   // 48 байтів: назва підсистеми
    uint64_t hdr_offset;      // 8 байтів: фізичний зсув на пристрої
    uint8_t  padding[184];    // 184 байти: зарезервовано
    uint8_t  csum[64];        // 64 байти: контрольна сума
    uint8_t  pad_to_4k[3584]; // 3584 байти: доповнення до сторінки 4096 байтів
};
static_assert(sizeof(HeaderDisk) == LUKS2_HDR_SIZE, "Розмір HeaderDisk мусить дорівнювати 4096 байтам");
