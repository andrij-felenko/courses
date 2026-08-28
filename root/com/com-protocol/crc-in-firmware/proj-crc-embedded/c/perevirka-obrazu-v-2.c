    uint8_t  buf[256];                          /* єдина плата оперативкою на весь образ */
    uint32_t off = SLOT_BASE + sizeof(img_header);   /* зміщення у зовнішній флеші */
    while (left) {
        uint32_t chunk = left > sizeof buf ? (uint32_t)sizeof buf : left;
        spi_flash_read(off, buf, chunk);
        crc32_feed(&c, buf, chunk);
        off  += chunk;
        left -= chunk;
        watchdog_kick();
    }
