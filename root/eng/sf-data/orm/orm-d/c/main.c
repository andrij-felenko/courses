#include <stdio.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int id;
    char username[32];
    char email[64];
} user_record_t;

typedef struct {
    user_record_t current;
    user_record_t snapshot; // Початковий знімок для Dirty Checking
    bool is_dirty;
} persistence_context_entry_t;

void check_and_save(persistence_context_entry_t *entry) {
    if (strcmp(entry->current.username, entry->snapshot.username) != 0 ||
        strcmp(entry->current.email, entry->snapshot.email) != 0) {
        entry->is_dirty = true;
        printf("[SQL] UPDATE users SET username='%s', email='%s' WHERE id=%d;\n",
               entry->current.username, entry->current.email, entry->current.id);
        entry->snapshot = entry->current; // Синхронізація знімка
    } else {
        printf("[No-Op] Сутність id=%d не змінювалася. SQL запит пропущено.\n", entry->current.id);
    }
}
