typedef enum { SRAM, SDRAM, NOR, NAND_BULK, EEPROM_FRAM } mem_t;

typedef struct {
    bool   nonvolatile;   // мусить пережити вимкнення?
    bool   exec_in_place;  // виконувати код напряму (XIP)?
    bool   byte_writes;    // дрібні побайтові уставки (не блоками)?
    size_t bytes;          // потрібний обсяг
} need_t;

mem_t pick_memory(need_t n) {
    if (!n.nonvolatile)                       // робочі дані → летка RAM
        return (n.bytes <= 256 * 1024) ? SRAM : SDRAM;
    if (n.exec_in_place)                       // код на місці → лише NOR
        return NOR;
    if (n.byte_writes && n.bytes < 64 * 1024)  // дрібні часті уставки
        return EEPROM_FRAM;
    return NAND_BULK;                          // гори файлів і медіа
}
