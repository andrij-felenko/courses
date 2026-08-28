#include <stddef.h>
#include <stdint.h>

typedef struct worm_context worm_context_t;

/* Ініціалізація клієнта журналу аудиту */
int worm_audit_init(worm_context_t** ctx, const char* storage_path, const uint8_t* master_key_32b);

/* Атомарний запис події з оновленням геш-ланцюга та просуванням ключа */
int worm_audit_append(worm_context_t* ctx, const uint8_t* payload, size_t length, uint64_t* out_seq);

/* Синхронізація буферів на енергонезалежний носій (fsync/O_SYNC) */
int worm_audit_flush(worm_context_t* ctx);

/* Верифікація діапазону записів на предмет незмінності та коректності підписів */
int worm_audit_verify(const char* log_file_path, const uint8_t* base_key_32b, uint64_t from_seq, uint64_t to_seq);

/* Звільнення ресурсів та безпечне затирання секретів у пам'яті */
void worm_audit_close(worm_context_t* ctx);
