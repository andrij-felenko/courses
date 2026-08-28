// Записати EC-заголовок у щойно стертий блок.
static int write_ec_hdr(uint16_t b, uint32_t counter) {
    ec_hdr_t *h = (ec_hdr_t *)pbuf;
    memset(pbuf, 0xFF, PAGE_SIZE);         // решта сторінки лишається «стертою»
    h->magic = EC_MAGIC;
    h->ec    = counter;
    h->crc   = crc32(h, sizeof *h - 4);
    return flash_write_page(b, EC_PAGE, pbuf);
}

// Стерти блок і повернути його у вільний пул.
static int free_block(uint16_t b) {
    if (flash_erase(b) != 0)   { state[b] = BS_BAD; return -1; }   // не стерся — не віримо
    ec[b]++;                                                        // стирання сталося — рахуємо
    if (write_ec_hdr(b, ec[b]) != 0) { state[b] = BS_BAD; return -1; }
    state[b] = BS_FREE;
    heap_push(b);
    return 0;
}
