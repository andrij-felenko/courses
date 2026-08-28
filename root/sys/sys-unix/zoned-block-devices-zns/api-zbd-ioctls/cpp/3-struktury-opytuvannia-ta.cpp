// У C++ вирівнювання та масив зон обробляються через динамічний буфер або std::vector
struct blk_zone_report {
    std::uint64_t sector;   // Початковий сектор (LBA), з якого починати звіт
    std::uint32_t nr_zones; // Вхід: розмір масиву; Вихід: повернуто зон
    std::uint32_t flags;    // Прапорці фільтрації звіту
    struct blk_zone zones[0]; // Динамічний контент зон
};

struct blk_zone {
    std::uint64_t start;    // Початковий сектор зони (у 512-байтових одиницях)
    std::uint64_t len;      // Фізичний розмір зони у секторах (Zone Size)
    std::uint64_t wp;       // Поточна позиція вказівника запису Write Pointer
    std::uint8_t  type;     // Тип зони (Conventional або SeqWrite)
    std::uint8_t  cond;     // Поточний стан зони (Empty, Open, Full тощо)
    std::uint8_t  non_seq;  // Прапорець непослідовного запису
    std::uint8_t  reset;    // Прапорець вимоги скидання зони
    std::uint8_t  resv[4];  // Резервні байти вирівнювання
    std::uint64_t capacity; // Дійсна ємність зони у секторах (Zone Capacity)
    std::uint8_t  reserved[24]; // Фіксований падінг структури
};
