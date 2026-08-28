#define FLASH_PAGE 256u

void flash_write(uint32_t addr, const uint8_t *data, uint32_t len) {
    while (len > 0) {
        uint32_t page_off = addr % FLASH_PAGE;      // де ми в поточній сторінці
        uint32_t chunk    = FLASH_PAGE - page_off;  // скільки влізе до її кінця
        if (chunk > len)
            chunk = len;                            // останній шматок — коротший
        flash_page_program(addr, data, chunk);      // сам чекає зайнятості
        addr += chunk;
        data += chunk;
        len  -= chunk;
    }
}
