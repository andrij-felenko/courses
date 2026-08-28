#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

// Елемент вільного списку із суворим вирівнюванням
typedef union SlotNode {
    union SlotNode* next;
    _Alignas(max_align_t) char raw_bytes[64]; // Буфер під структуру фіксованого розміру
} SlotNode;

typedef struct {
    SlotNode* storage;
    SlotNode* free_head;
    size_t capacity;
    size_t item_size;
} ObjectPoolC;

// Демонстраційна сутність у стилі C
typedef struct {
    uint64_t id;
    char* token; // Динамічний ресурс, що вимагає ручного звільнення
} SessionC;

// Явний аналог конструктора
int session_construct(SessionC* s, uint64_t id, const char* token) {
    s->id = id;
    size_t len = strlen(token) + 1;
    s->token = (char*)malloc(len);
    if (!s->token) {
        return -1;
    }
    memcpy(s->token, token, len);
    printf("  [+] C Session #%llu створено (токен: %s)\n", (unsigned long long)s->id, s->token);
    return 0;
}

// Явний аналог деструктора
void session_destruct(SessionC* s) {
    printf("  [-] C Session #%llu знищено (пам'ять токена звільнено)\n", (unsigned long long)s->id);
    free(s->token);
    s->token = NULL;
}

int pool_init(ObjectPoolC* pool, size_t capacity, size_t item_size) {
    if (item_size > sizeof(SlotNode)) {
        return -1; // Структура занадто велика для наявного розміру слота
    }
    pool->capacity = capacity;
    pool->item_size = item_size;
    pool->storage = (SlotNode*)malloc(capacity * sizeof(SlotNode));
    if (!pool->storage) return -1;

    pool->free_head = NULL;
    for (size_t i = 0; i < capacity; ++i) {
        pool->storage[i].next = pool->free_head;
        pool->free_head = &pool->storage[i];
    }
    return 0;
}

void* pool_alloc_raw(ObjectPoolC* pool) {
    if (!pool->free_head) return NULL;
    SlotNode* node = pool->free_head;
    pool->free_head = node->next;
    return (void*)node;
}

void pool_free_raw(ObjectPoolC* pool, void* ptr) {
    if (!ptr) return;
    SlotNode* node = (SlotNode*)ptr;
    node->next = pool->free_head;
    pool->free_head = node;
}

void pool_destroy(ObjectPoolC* pool) {
    free(pool->storage);
    pool->storage = NULL;
    pool->free_head = NULL;
}

int main(void) {
    ObjectPoolC pool;
    if (pool_init(&pool, 2, sizeof(SessionC)) != 0) {
        return 1;
    }

    printf("1. Ручне виділення сирої адреси та ініціалізація:\n");
    SessionC* s1 = (SessionC*)pool_alloc_raw(&pool);
    session_construct(s1, 101, "tok_auth_abc");

    SessionC* s2 = (SessionC*)pool_alloc_raw(&pool);
    session_construct(s2, 102, "tok_auth_xyz");

    printf("2. Ручне знищення полів та повернення слота в пул:\n");
    session_destruct(s1);
    pool_free_raw(&pool, s1);

    session_destruct(s2);
    pool_free_raw(&pool, s2);

    printf("3. Повторне використання пам'яті без звернення до malloc:\n");
    SessionC* s3 = (SessionC*)pool_alloc_raw(&pool);
    session_construct(s3, 103, "tok_auth_reused");

    session_destruct(s3);
    pool_free_raw(&pool, s3);

    pool_destroy(&pool);
    return 0;
}
