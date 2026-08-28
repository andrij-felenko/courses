struct alignas(1) HeaderDisk {
    char     magic[6];        // Сигнатура "LUKS\xba\xbe" або "SKUL\xba\xbe"
    uint16_t version;         // Версія формату: 0x0002
    uint64_t hdr_size;        // Розмір зони метаданих у байтах (4 МіБ)
    uint64_t seqid;           // Монотонний лічильник транзакцій
    char     label[48];       // Мітка тома (ASCII/UTF-8)
    char     csum_alg[32];    // Алгоритм гешу ("sha256", "sha512", "crc32")
    uint8_t  salt[64];        // Криптографічна сіль
    char     uuid[44];        // Унікальний ідентифікатор UUID
    char     subsystem[48];   // Назва підсистеми
    uint64_t hdr_offset;      // Фізичний зсув заголовка на носії
    uint8_t  padding[184];    // Вирівнювання до поля контрольної суми
    uint8_t  csum[64];        // Контрольна сума дескриптора та JSON
    uint8_t  pad_to_4k[3584]; // Доповнення до розміру сторінки 4096 байтів
};
static_assert(sizeof(HeaderDisk) == 4096, "Розмір HeaderDisk мусить дорівнювати 4096 байтам");
