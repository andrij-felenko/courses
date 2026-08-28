#include <linux/uuid.h>

/* Оголошення та ініціалізація бінарного GUID з рядка */
guid_t my_guid;
int ret = guid_parse("9DBB5994-A997-11DA-B012-B622A1EF5492", &my_guid);

/* Порівняння двох бінарних GUID */
if (guid_equal(&guid1, &guid2)) {
    /* GUID збігаються */
}

/* Перевірка на порожній (нульовий) GUID */
if (guid_is_null(&my_guid)) {
    /* GUID складається з усіх нулів */
}

/* Експорт бінарного GUID у буфер */
u8 buffer[16];
export_guid(buffer, &my_guid);
