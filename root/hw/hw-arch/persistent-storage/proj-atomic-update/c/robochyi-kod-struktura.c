// Обчислити CRC-32 усього запису, крім самого поля crc.
static uint32_t record_crc(const Record *r) {
    // Сума покриває seq і data, але НЕ поле crc (останні 4 байти).
    return crc32(r, sizeof(Record) - sizeof(r->crc));
}

int config_save(const Config *cfg) {
    int cur = active_slot();          // чинний слот (0/1), або -1 якщо порожньо
    int next;
    uint32_t next_seq;

    if (cur < 0) {
        // Перший у житті запис: чинного ще нема. Пишемо в слот A,
        // з якого починається відлік поколінь.
        next     = SLOT_A;
        next_seq = 1;
    } else {
        next     = cur ^ 1;           // писати в ІНШИЙ слот
        next_seq = read_seq(cur) + 1; // на одне покоління новіший
    }

    Record r;
    memset(&r, 0, sizeof(r));         // занулити «дірки» вирівнювання структури
    r.seq  = next_seq;
    r.data = *cfg;
    r.crc  = record_crc(&r);          // печатка — в останню чергу

    flash_erase_slot(next);           // готуємо чистий запасний слот
    flash_write_slot(next, &r, sizeof(r)); // цілком записуємо новий запис
    // Аж ТЕПЕР новий запис існує повністю й проходитиме перевірку CRC.
    // Слот cur увесь цей час недоторканий — старі дані ані на мить не гинули.

    // Необов'язково, але корисно: перечитати й звірити CRC записаного,
    // щоб упіймати збій запису одразу, а не при наступному ввімкненні.
    Record check;
    flash_read_slot(next, &check);
    if (record_crc(&check) != check.crc) {
        return -1;                    // запис не вдався — чинним лишився cur
    }
    return 0;
}
