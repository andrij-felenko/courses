#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t tag;
    const uint8_t *value;
    size_t length;
    size_t total_tlv_size;
} DerElement;

/* Зчитування чергового вузла TLV з потоку пам'яті */
bool der_read_element(const uint8_t *data, size_t max_len, DerElement *elem) {
    if (!data || max_len < 2 || !elem) return false;

    elem->tag = data[0];
    size_t offset = 1;
    size_t val_len = 0;

    if ((data[offset] & 0x80) == 0) {
        /* Коротка форма: довжина 0..127 байтів */
        val_len = data[offset];
        offset += 1;
    } else {
        /* Довга форма: перший байт містить кількість байтів довжини */
        size_t len_octets = data[offset] & 0x7F;
        offset += 1;
        if (len_octets == 0 || len_octets > sizeof(size_t) || offset + len_octets > max_len) {
            return false;
        }
        val_len = 0;
        for (size_t i = 0; i < len_octets; ++i) {
            val_len = (val_len << 8) | data[offset + i];
        }
        offset += len_octets;
    }

    if (offset + val_len > max_len) return false;

    elem->value = &data[offset];
    elem->length = val_len;
    elem->total_tlv_size = offset + val_len;
    return true;
}

/* Пошук блоку SubjectPublicKeyInfo всередині TBSCertificate */
bool der_find_spki(const uint8_t *cert_der, size_t cert_len, const uint8_t **spki_ptr, size_t *spki_len) {
    DerElement cert_seq, tbs_seq;
    if (!der_read_element(cert_der, cert_len, &cert_seq) || cert_seq.tag != 0x30) return false;
    if (!der_read_element(cert_seq.value, cert_seq.length, &tbs_seq) || tbs_seq.tag != 0x30) return false;

    /* Обхід полів всередині TBSCertificate */
    const uint8_t *cursor = tbs_seq.value;
    size_t remaining = tbs_seq.length;
    int field_index = 0;

    while (remaining > 0) {
        DerElement elem;
        if (!der_read_element(cursor, remaining, &elem)) return false;

        /* Поле 0 може бути версією [0] (0xA0) */
        if (field_index == 0 && elem.tag == 0xA0) {
            /* Пропускаємо явний тег версії */
            cursor += elem.total_tlv_size;
            remaining -= elem.total_tlv_size;
            continue;
        }

        /* 
         * Послідовність полів:
         * 0: serialNumber (INTEGER 0x02)
         * 1: signature (SEQUENCE 0x30)
         * 2: issuer (SEQUENCE 0x30)
         * 3: validity (SEQUENCE 0x30)
         * 4: subject (SEQUENCE 0x30)
         * 5: SubjectPublicKeyInfo (SEQUENCE 0x30)
         */
        if (field_index == 5 && elem.tag == 0x30) {
            *spki_ptr = cursor;
            *spki_len = elem.total_tlv_size;
            return true;
        }

        cursor += elem.total_tlv_size;
        remaining -= elem.total_tlv_size;
        field_index++;
    }
    return false;
}
