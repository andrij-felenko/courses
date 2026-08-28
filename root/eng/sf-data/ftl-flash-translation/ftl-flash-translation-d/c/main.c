// LPN — логічний номер сторінки (що дала OS), PPN — фізичний (де реально лежить)
uint32_t map[N_LOGICAL];                 // таблиця відображення: map[LPN] = PPN

void ftl_write(uint32_t lpn, const void *data) {
    uint32_t old_ppn = map[lpn];         // де лежала попередня версія
    uint32_t new_ppn = alloc_free_page();// беремо свіжу, вже стерту сторінку
    flash_program(new_ppn, data);        // пишемо НЕ поверх старої
    map[lpn] = new_ppn;                   // переставляємо один вказівник
    if (old_ppn != NONE)
        mark_invalid(old_ppn);           // стара версія стала сміттям
}
