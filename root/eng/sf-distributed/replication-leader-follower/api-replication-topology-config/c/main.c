#include <stdint.h>
#include <stddef.h>

typedef struct {
    const char*    datacenter_id;
    uint64_t       logical_timestamp;
    const uint8_t* payload;
    size_t         payload_len;
} MutationRecord;

typedef struct {
    uint8_t* merged_payload;
    size_t   merged_payload_len;
    int      should_delete; /* 1 = перетворити на Tombstone, 0 = зберегти */
} ConflictResolutionResult;

/**
 * @brief Точка входу користувацького злиття конфліктів (C ABI)
 * @param key Ключ сутності, на якій виник конфлікт
 * @param key_len Довжина ключа в байтах
 * @param local Поточний локальний стан рядка
 * @param remote Вхідна мутація з віддаленого датацентру
 * @param out_result Буфер для результуючого об'єднаного значення
 * @return 0 при успіху, ненульовий код помилки
 */
int resolve_write_conflict(
    const char*                     key,
    size_t                          key_len,
    const MutationRecord*           local,
    const MutationRecord*           remote,
    ConflictResolutionResult*       out_result
);
