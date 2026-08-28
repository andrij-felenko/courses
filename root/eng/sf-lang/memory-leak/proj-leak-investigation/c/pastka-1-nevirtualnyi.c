#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Симуляція поліморфізму мовою C через таблицю функцій */
typedef struct Base Base;
typedef struct BaseVTable {
    void (*destroy)(Base *self);
} BaseVTable;

struct Base {
    const BaseVTable *vptr;
    int id;
};

typedef struct Derived {
    Base base;
    char *payload; /* Динамічний буфер */
} Derived;

void base_destroy(Base *self) {
    /* Базовий деструктор не знає про payload нащадка */
    printf("[C Base] Звільнення базової частини id=%d\n", self->id);
    free(self);
}

void derived_destroy(Base *self) {
    Derived *d = (Derived *)self;
    printf("[C Derived] Звільнення буфера payload\n");
    free(d->payload);
    free(d);
}

const BaseVTable base_vtable = { base_destroy };
const BaseVTable derived_vtable = { derived_destroy };

Base *create_derived(int id, const char *text) {
    Derived *d = (Derived *)malloc(sizeof(Derived));
    if (!d) return NULL;
    d->base.vptr = &derived_vtable;
    d->base.id = id;
    d->payload = (char *)malloc(strlen(text) + 1);
    if (!d->payload) { free(d); return NULL; }
    strcpy(d->payload, text);
    return (Base *)d;
}

int main(void) {
    Base *obj = create_derived(101, "Поліморфне повідомлення");
    
    /* ПОМИЛКА: прямий виклик base_destroy замість диспетчеризації через vptr */
    base_destroy(obj); /* d->payload витікає! */
    return 0;
}
