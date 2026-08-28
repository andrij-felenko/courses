struct blk_zone_report {
    __u64   sector;         // Початковий сектор для запиту звіту
    __u32   nr_zones;       // Вхід: розмір масиву; Вихід: повернута кількість зон
    __u32   flags;          // Додаткові прапорці запиту
    struct blk_zone zones[]; // Гнучкий масив структур опису зон
};

struct blk_zone {
    __u64   start;          // Початковий сектор зони в LBA
    __u64   len;            // Довжина зони у секторах (наприклад, 524288)
    __u64   wp;             // Поточна позиція покажчика запису (Write Pointer)
    __u8    type;           // Тип зони (BLK_ZONE_TYPE_SEQWRITE_REQ)
    __u8    cond;           // Стан зони (EMPTY, IMP_OPEN, EXP_OPEN, CLOSED, READONLY, FULL, OFFLINE)
    __u8    non_seq;        // Зона обслуговується ресурсом непослідовного запису
    __u8    reset;          // Контролер радить скинути цю зону
    __u8    resv[4];
    __u64   capacity;       // Корисна ємність зони в секторах (може бути меншою за len)
    __u8    reserved[24];   // Резерв під майбутні розширення стандарту
};

struct blk_zone_range {
    __u64   sector;         // Початковий сектор зони для керування
    __u64   nr_sectors;     // Кількість секторів (має бути кратною chunk_sectors)
};
