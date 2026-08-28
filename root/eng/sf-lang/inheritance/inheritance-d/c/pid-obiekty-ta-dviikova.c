#include <stdio.h>
#include <stddef.h>

/* Базовий під-об'єкт */
typedef struct {
    int id;
    int flags;
} Base;

/* Похідна структура: базовий блок стоїть строго першим */
typedef struct {
    Base base;         /* Зсув 0 байтів */
    double score;      /* Зсув 8 байтів (після вирівнювання) */
    int extra;         /* Зсув 16 байтів */
} Derived;

void print_base(const Base* b) {
    printf("Base id: %d, flags: 0x%X\n", b->id, b->flags);
}

int main(void) {
    Derived d;
    d.base.id = 42;
    d.base.flags = 0x01;
    d.score = 99.5;
    d.extra = 7;

    /* Безпечне приведення вказівника: адреса d збігається з адресою d.base */
    const Base* b_ptr = (const Base*)&d;
    print_base(b_ptr);

    printf("Зсув base:  %zu B\n", offsetof(Derived, base));
    printf("Зсув score: %zu B\n", offsetof(Derived, score));
    return 0;
}
