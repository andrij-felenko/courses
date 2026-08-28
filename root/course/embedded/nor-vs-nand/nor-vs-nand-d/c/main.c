// сектор 4 КБ; хочемо змінити один байт за зміщенням off
#define SECTOR      4096
uint8_t buf[SECTOR];

void nor_change_one_byte(uint32_t sector_addr, uint32_t off, uint8_t val) {
    nor_read(sector_addr, buf, SECTOR);   // 1) вичитати весь сектор у RAM
    buf[off] = val;                       // 2) поправити один байт у копії
    nor_write_enable();                   // 3) дозвіл на запис
    nor_sector_erase(sector_addr);        // 4) стерти весь сектор (десятки мс!)
    nor_wait_busy();                      //    чекати, поки чип звільниться
    for (uint32_t p = 0; p < SECTOR; p += 256) {  // 5) записати всі 16 сторінок
        nor_write_enable();
        nor_page_program(sector_addr + p, buf + p, 256);
        nor_wait_busy();
    }
}
