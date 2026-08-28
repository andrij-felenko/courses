// Стерти слот повністю: після цього весь слот читається як 0xFF.
// Стирання йде цілими блоками — тому слот вирівняний по межі блоку.
void flash_erase_slot(int slot);

// Записати buf у слот від його початку. len має бути кратний
// зернистості запису чипа (див. пастку про вирівнювання).
void flash_write_slot(int slot, const void *buf, size_t len);

// Прочитати весь запис зі слоту в out.
void flash_read_slot(int slot, Record *out);
