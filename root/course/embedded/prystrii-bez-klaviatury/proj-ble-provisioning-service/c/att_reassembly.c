#include "att_reassembly.h"

#include <string.h>

uint16_t att_mtu_negotiate(uint16_t client_mtu)
{
    /* Менше за базовий MTU клієнт запропонувати не може — такий запит
       некоректний, і специфікація велить триматися базового значення. */
    if (client_mtu < ATT_MTU_DEFAULT) {
        client_mtu = ATT_MTU_DEFAULT;
    }
    return client_mtu < ATT_MTU_MAX ? client_mtu : ATT_MTU_MAX;
}

uint16_t att_mtu_payload(uint16_t mtu)
{
    return (uint16_t)(mtu - ATT_HEADER_SIZE);
}

void att_reasm_cancel(att_reasm_t *r)
{
    /* Фрагменти могли нести зашифрований пароль — затираємо весь буфер. */
    memset(r->buffer, 0, sizeof(r->buffer));
    r->length = 0;
    r->char_uuid = 0;
    r->active = false;
}

uint8_t att_reasm_prepare(att_reasm_t *r, uint16_t char_uuid, uint16_t offset,
                          const uint8_t *value, size_t len)
{
    if (!r->active) {
        r->active = true;
        r->char_uuid = char_uuid;
        r->length = 0;
    }

    /* Черга підготовлених записів одна на зʼєднання: мішати дві характеристики
       в ній ми не даємо, щоб пів-пакета сесії не приїхало в конфігурацію. */
    if (r->char_uuid != char_uuid) {
        return ATT_ERR_UNLIKELY;
    }

    /* Клієнт нумерує фрагменти зміщенням. Приймаємо лише суцільний потік:
       дірка або перекриття означають загублений чи повторений кадр. */
    if (offset != r->length) {
        return ATT_ERR_INVALID_OFFSET;
    }

    if (len > (size_t)(ATT_REASM_CAPACITY - r->length)) {
        return ATT_ERR_PREPARE_QUEUE_FULL;
    }

    memcpy(r->buffer + r->length, value, len);
    r->length = (uint16_t)(r->length + len);
    return ATT_ERR_NONE;
}

uint8_t att_reasm_execute(att_reasm_t *r, bool commit,
                          uint16_t *out_uuid, const uint8_t **out_value, size_t *out_len)
{
    *out_uuid = 0;
    *out_value = NULL;
    *out_len = 0;

    if (!commit) {
        att_reasm_cancel(r);
        return ATT_ERR_NONE;        /* скасування — законна дія, не помилка */
    }

    if (!r->active) {
        return ATT_ERR_NONE;        /* порожня черга: виконувати нічого */
    }

    if (r->length == 0) {
        att_reasm_cancel(r);
        return ATT_ERR_INVALID_ATTR_LEN;
    }

    *out_uuid = r->char_uuid;
    *out_value = r->buffer;
    *out_len = r->length;
    r->active = false;              /* значення віддали; буфер затре наступний prepare */
    return ATT_ERR_NONE;
}
