#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int id;
    char name[32];
} Session;

typedef struct {
    Session* data;
    size_t size;
    size_t capacity;
} SessionVector;

void vector_init(SessionVector* v, size_t cap) {
    v->data = (Session*)malloc(cap * sizeof(Session));
    v->size = 0;
    v->capacity = cap;
}

void vector_push(SessionVector* v, int id, const char* name) {
    if (v->size >= v->capacity) {
        size_t new_cap = v->capacity * 2;
        Session* new_data = (Session*)malloc(new_cap * sizeof(Session));
        memcpy(new_data, v->data, v->size * sizeof(Session));
        free(v->data); // Старий буфер звільнено!
        v->data = new_data;
        v->capacity = new_cap;
    }
    v->data[v->size].id = id;
    strncpy(v->data[v->size].name, name, sizeof(v->data[v->size].name) - 1);
    v->data[v->size].name[sizeof(v->data[v->size].name) - 1] = '\0';
    v->size++;
}

int main(void) {
    SessionVector vec;
    vector_init(&vec, 2);
    vector_push(&vec, 101, "AdminAuth");
    vector_push(&vec, 102, "UserGuest");

    // Зберігаємо прямий вказівник на перший елемент
    Session* primary = &vec.data[0];

    // Додавання третього елемента викликає релокацію та free(v->data)
    vector_push(&vec, 103, "ServiceWorker");

    // Помилка: primary вказує на звільнений буфер (Heap-Use-After-Free)
    printf("Сесія ID: %d, Назва: %s\n", primary->id, primary->name);

    free(vec.data);
    return 0;
}
