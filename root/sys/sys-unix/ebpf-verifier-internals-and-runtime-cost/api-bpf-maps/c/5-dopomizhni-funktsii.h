/* Пошук вказівника на значення за адресою ключа. Повертає NULL якщо ключ відсутній */
void *bpf_map_lookup_elem(struct bpf_map *map, const void *key);

/* Вставка або оновлення значення. Повертає 0 у разі успіху або від'ємний код помилки */
long bpf_map_update_elem(struct bpf_map *map, const void *key, const void *value, __u64 flags);

/* Видалення ключа з карти. Повертає 0 або від'ємний код помилки */
long bpf_map_delete_elem(struct bpf_map *map, const void *key);

/* Пряме копіювання події в кільцевий буфер Ring Buffer */
long bpf_ringbuf_output(void *ringbuf, void *data, __u64 size, __u64 flags);

/* Резервування слоту пам'яті в Ring Buffer з нульовим копіюванням */
void *bpf_ringbuf_reserve(void *ringbuf, __u64 size, __u64 flags);

/* Публікація зарезервованого запису для зчитування процесом простору користувача */
void bpf_ringbuf_submit(void *data, __u64 flags);

/* Скасування зарезервованого запису у разі виникнення помилки */
void bpf_ringbuf_discard(void *data, __u64 flags);
