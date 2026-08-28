#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ENTITIES 32
#define MAX_NAME_LEN 64
#define MAX_EMAIL_LEN 64

// 1. Чиста доменна сутність
typedef struct {
    uint32_t id;
    char name[MAX_NAME_LEN];
    char email[MAX_EMAIL_LEN];
} user_entity_t;

typedef enum {
    STATE_CLEAN,
    STATE_NEW,
    STATE_DIRTY,
    STATE_DELETED
} entity_state_t;

typedef struct {
    user_entity_t *entity;
    user_entity_t snapshot; // Початковий стан для Dirty Checking
    entity_state_t state;
} tracked_user_t;

typedef struct {
    tracked_user_t tracked[MAX_ENTITIES];
    size_t count;
} unit_of_work_t;

void uow_init(unit_of_work_t *uow) {
    uow->count = 0;
}

// Завантаження сутності в Identity Map
user_entity_t* uow_register_clean(unit_of_work_t *uow, uint32_t id, const char *name, const char *email) {
    for (size_t i = 0; i < uow->count; ++i) {
        if (uow->tracked[i].entity->id == id) {
            return uow->tracked[i].entity; // Повертаємо існуючий екземпляр з кешу L1
        }
    }

    if (uow->count >= MAX_ENTITIES) return NULL;

    user_entity_t *user = (user_entity_t*)malloc(sizeof(user_entity_t));
    user->id = id;
    strncpy(user->name, name, MAX_NAME_LEN - 1);
    strncpy(user->email, email, MAX_EMAIL_LEN - 1);

    tracked_user_t *tr = &uow->tracked[uow->count++];
    tr->entity = user;
    tr->snapshot = *user; // Зберігаємо точну копію початкового стану
    tr->state = STATE_CLEAN;

    return user;
}

void uow_register_new(unit_of_work_t *uow, user_entity_t *user) {
    if (uow->count >= MAX_ENTITIES) return;
    tracked_user_t *tr = &uow->tracked[uow->count++];
    tr->entity = user;
    tr->state = STATE_NEW;
}

void uow_register_deleted(unit_of_work_t *uow, user_entity_t *user) {
    for (size_t i = 0; i < uow->count; ++i) {
        if (uow->tracked[i].entity == user) {
            uow->tracked[i].state = STATE_DELETED;
            return;
        }
    }
}

// Перевірка змін (Dirty Checking) та формування SQL-батчу
void uow_commit(unit_of_work_t *uow) {
    printf("=== Unit of Work: Початок транзакції (BEGIN) ===\n");

    for (size_t i = 0; i < uow->count; ++i) {
        tracked_user_t *tr = &uow->tracked[i];

        if (tr->state == STATE_NEW) {
            printf("[INSERT] INTO users (id, name, email) VALUES (%u, '%s', '%s');\n",
                   tr->entity->id, tr->entity->name, tr->entity->email);
            tr->snapshot = *tr->entity;
            tr->state = STATE_CLEAN;
        } else if (tr->state == STATE_CLEAN) {
            // Виконання Dirty Checking
            bool name_changed = strcmp(tr->entity->name, tr->snapshot.name) != 0;
            bool email_changed = strcmp(tr->entity->email, tr->snapshot.email) != 0;

            if (name_changed || email_changed) {
                printf("[UPDATE] users SET name = '%s', email = '%s' WHERE id = %u;\n",
                       tr->entity->name, tr->entity->email, tr->entity->id);
                tr->snapshot = *tr->entity; // Оновлюємо знімок
            }
        } else if (tr->state == STATE_DELETED) {
            printf("[DELETE] FROM users WHERE id = %u;\n", tr->entity->id);
        }
    }

    printf("=== Unit of Work: Транзакцію зафіксовано (COMMIT) ===\n");
}
