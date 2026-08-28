#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

#define BLOCK_SIZE 64

typedef enum {
    LOCK_NL = 0,
    LOCK_PR = 1,
    LOCK_EX = 2
} lock_mode_t;

static const char *mode_str(lock_mode_t m) {
    switch (m) {
        case LOCK_NL: return "NL (Unlocked)";
        case LOCK_PR: return "PR (Protected Read / Shared)";
        case LOCK_EX: return "EX (Exclusive)";
        default:      return "UNKNOWN";
    }
}

/* Спільний блоковий накопичувач */
typedef struct {
    char data[BLOCK_SIZE];
    pthread_mutex_t disk_mutex;
} shared_storage_t;

/* Стан блокування ресурсу в DLM */
typedef struct {
    pthread_mutex_t lock_mutex;
    pthread_cond_t  lock_cv;
    lock_mode_t     granted_mode;
    int             owner_node_id; /* -1 якщо вільно або декілька PR */
    int             pr_holders_count;
} dlm_resource_t;

/* Локальний стан вузла */
typedef struct {
    int              node_id;
    char             local_cache[BLOCK_SIZE];
    bool             cache_valid;
    bool             cache_dirty;
    lock_mode_t      held_mode;
    dlm_resource_t  *res;
    shared_storage_t *disk;
} cluster_node_t;

/* Ініціалізація компонентів */
void storage_init(shared_storage_t *s) {
    memset(s->data, 0, BLOCK_SIZE);
    snprintf(s->data, BLOCK_SIZE, "Початкові дані на диску");
    pthread_mutex_init(&s->disk_mutex, NULL);
}

void dlm_init(dlm_resource_t *res) {
    pthread_mutex_init(&res->lock_mutex, NULL);
    pthread_cond_init(&res->lock_cv, NULL);
    res->granted_mode = LOCK_NL;
    res->owner_node_id = -1;
    res->pr_holders_count = 0;
}

void node_init(cluster_node_t *node, int id, dlm_resource_t *res, shared_storage_t *disk) {
    node->node_id = id;
    memset(node->local_cache, 0, BLOCK_SIZE);
    node->cache_valid = false;
    node->cache_dirty = false;
    node->held_mode = LOCK_NL;
    node->res = res;
    node->disk = disk;
}

/* Обробник BAST (Blocking AST): примусове скидання кешу та пониження режиму */
void handle_bast(cluster_node_t *node, lock_mode_t requested_mode) {
    printf("[Вузол %d] << Отримано BAST: інший вузол вимагає %s >>\n",
           node->node_id, mode_str(requested_mode));

    if (node->cache_dirty) {
        printf("[Вузол %d] BAST: Скидання брудного кешу на диск: \"%s\"\n",
               node->node_id, node->local_cache);
        pthread_mutex_lock(&node->disk->disk_mutex);
        memcpy(node->disk->data, node->local_cache, BLOCK_SIZE);
        pthread_mutex_unlock(&node->disk->disk_mutex);
        node->cache_dirty = false;
    }

    if (requested_mode == LOCK_PR && node->held_mode == LOCK_EX) {
        printf("[Вузол %d] BAST: Добровільне пониження блокування EX -> PR\n", node->node_id);
        node->held_mode = LOCK_PR;
    } else if (requested_mode == LOCK_EX) {
        printf("[Вузол %d] BAST: Повна інвалідація кешу та звільнення до NL\n", node->node_id);
        node->held_mode = LOCK_NL;
        node->cache_valid = false;
    }
}

/* Запит на отримання блокування через DLM */
void dlm_acquire(cluster_node_t *node, lock_mode_t target_mode, cluster_node_t *other_node) {
    pthread_mutex_lock(&node->res->lock_mutex);

    printf("[Вузол %d] Запит блокування %s (поточний утримуваний: %s)\n",
           node->node_id, mode_str(target_mode), mode_str(node->held_mode));

    while (1) {
        if (target_mode == LOCK_PR) {
            if (node->res->granted_mode == LOCK_NL || node->res->granted_mode == LOCK_PR) {
                node->res->granted_mode = LOCK_PR;
                node->res->pr_holders_count++;
                node->held_mode = LOCK_PR;
                printf("[Вузол %d] >> CAST: Надано режим PR (читачів: %d) <<\n",
                       node->node_id, node->res->pr_holders_count);
                break;
            } else if (node->res->granted_mode == LOCK_EX) {
                /* Конфлікт: викликаємо BAST на власнику EX */
                printf("[DLM] Конфлікт! Виклик BAST на Вузлі %d\n", other_node->node_id);
                handle_bast(other_node, LOCK_PR);
                node->res->granted_mode = LOCK_PR;
                node->res->owner_node_id = -1;
                node->res->pr_holders_count = 1; /* Вузол A понизився до PR */
                node->res->pr_holders_count++;   /* Вузол B отримує PR */
                node->held_mode = LOCK_PR;
                printf("[Вузол %d] >> CAST: Надано режим PR після деградації EX <<\n", node->node_id);
                break;
            }
        } else if (target_mode == LOCK_EX) {
            if (node->res->granted_mode == LOCK_NL) {
                node->res->granted_mode = LOCK_EX;
                node->res->owner_node_id = node->node_id;
                node->held_mode = LOCK_EX;
                printf("[Вузол %d] >> CAST: Надано режим EX <<\n", node->node_id);
                break;
            } else {
                /* Конфлікт із PR або чужим EX */
                printf("[DLM] Конфлікт для EX! Виклик BAST на Вузлі %d\n", other_node->node_id);
                handle_bast(other_node, LOCK_EX);
                node->res->granted_mode = LOCK_EX;
                node->res->owner_node_id = node->node_id;
                node->res->pr_holders_count = 0;
                node->held_mode = LOCK_EX;
                printf("[Вузол %d] >> CAST: Надано режим EX після витіснення <<\n", node->node_id);
                break;
            }
        }
        pthread_cond_wait(&node->res->lock_cv, &node->res->lock_mutex);
    }

    pthread_mutex_unlock(&node->res->lock_mutex);
}

/* Операції запису та читання */
void node_write(cluster_node_t *node, const char *new_text, cluster_node_t *other_node) {
    printf("\n--- [Вузол %d] Початок операції WRITE(\"%s\") ---\n", node->node_id, new_text);
    if (node->held_mode != LOCK_EX) {
        dlm_acquire(node, LOCK_EX, other_node);
    }
    snprintf(node->local_cache, BLOCK_SIZE, "%s", new_text);
    node->cache_valid = true;
    node->cache_dirty = true;
    printf("[Вузол %d] Запис у локальний Page Cache виконано (cache_dirty = true)\n", node->node_id);
}

void node_read(cluster_node_t *node, cluster_node_t *other_node) {
    printf("\n--- [Вузол %d] Початок операції READ() ---\n", node->node_id);
    if (node->held_mode == LOCK_NL) {
        dlm_acquire(node, LOCK_PR, other_node);
    }
    if (!node->cache_valid) {
        printf("[Вузол %d] Кеш невалідний! Читання блоку з фізичного LUN...\n", node->node_id);
        pthread_mutex_lock(&node->disk->disk_mutex);
        memcpy(node->local_cache, node->disk->data, BLOCK_SIZE);
        pthread_mutex_unlock(&node->disk->disk_mutex);
        node->cache_valid = true;
    } else {
        printf("[Вузол %d] Використання валідного локального кешу сторінок (RAM Hit)\n", node->node_id);
    }
    printf("[Вузол %d] Прочитані дані: \"%s\"\n", node->node_id, node->local_cache);
}

int main(void) {
    shared_storage_t disk;
    dlm_resource_t   res;
    cluster_node_t   node_a, node_b;

    storage_init(&disk);
    dlm_init(&res);
    node_init(&node_a, 1, &res, &disk);
    node_init(&node_b, 2, &res, &disk);

    printf("=== СТАРТ СИМУЛЯЦІЇ SHARED-DISK ТА DLM ===\n");

    /* Сценарій:
       1. Вузол A пише нові дані (захоплює EX, кешує в RAM без негайного скидання).
       2. Вузол B намагається прочитати дані (запитує PR).
       3. DLM ініціює BAST на Вузлі A -> Вузол A скидає кеш на диск -> DLM надає PR Вузлу B.
       4. Вузол B інвалідує свій кеш і читає свіжі дані з диска. */

    node_write(&node_a, "Оновлення блоку 42 від Вузла 1", &node_b);
    node_read(&node_b, &node_a);

    printf("\n=== ЗАВЕРШЕННЯ СИМУЛЯЦІЇ ===\n");
    return 0;
}
