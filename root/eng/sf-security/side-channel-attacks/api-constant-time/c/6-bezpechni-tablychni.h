/* Вибірка 8-бітного байта з таблиці довільного розміру */
uint8_t ct_lookup_u8(const uint8_t *table, size_t table_len, size_t secret_idx);

/* Вибірка 32-бітного слова з масиву */
uint32_t ct_lookup_u32(const uint32_t *table, size_t table_len, size_t secret_idx);

/* Вибірка 64-бітного слова з масиву */
uint64_t ct_lookup_u64(const uint64_t *table, size_t table_len, size_t secret_idx);

/* Копіювання елемента довільного фіксованого розміру elem_size з масиву */
void ct_lookup_element(void *dst, const void *table, size_t num_elems, size_t elem_size, size_t secret_idx);
