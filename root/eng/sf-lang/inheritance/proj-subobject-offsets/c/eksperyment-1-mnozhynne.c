#include <stdio.h>
#include <stddef.h>
#include <stdint.h>

/* Базовий інтерфейс A з віртуальною таблицею */
typedef struct BaseA_vtable {
    void (*funcA)(void* self);
} BaseA_vtable;

typedef struct {
    const BaseA_vtable* vptr_A;
    int a_val;
} BaseA;

/* Базовий інтерфейс B з віртуальною таблицею */
typedef struct BaseB_vtable {
    void (*funcB)(void* self);
} BaseB_vtable;

typedef struct {
    const BaseB_vtable* vptr_B;
    int b_val;
} BaseB;

/* Похідна структура: об'єднує BaseA, BaseB та власні поля */
typedef struct {
    BaseA a;      /* Під-об'єкт BaseA розташовано на зсуві 0 */
    BaseB b;      /* Під-об'єкт BaseB розташовано на зсуві offsetof(Derived, b) */
    int d_val;    /* Власне поле даних Derived */
} Derived;

static void derived_funcA(void* self) {
    Derived* d = (Derived*)self;
    printf("Derived::funcA виконано (d_val = %d)\n", d->d_val);
}

/* Thunk-функція для BaseB: коригує вказівник перед викликом методу */
static void derived_funcB_thunk(void* self) {
    /* Віднімаємо зсув під-об'єкта BaseB, щоб отримати адресу Derived */
    Derived* d = (Derived*)((char*)self - offsetof(Derived, b));
    printf("Derived::funcB через thunk виконано (d_val = %d)\n", d->d_val);
}

static const BaseA_vtable g_vtable_A = { derived_funcA };
static const BaseB_vtable g_vtable_B = { derived_funcB_thunk };

int main(void) {
    Derived obj;
    obj.a.vptr_A = &g_vtable_A;
    obj.a.a_val  = 100;

    obj.b.vptr_B = &g_vtable_B;
    obj.b.b_val  = 200;

    obj.d_val    = 300;

    Derived* p_derived = &obj;
    
    /* Розрахунок адрес під-об'єктів */
    BaseA* p_a = (BaseA*)((char*)p_derived + offsetof(Derived, a));
    BaseB* p_b = (BaseB*)((char*)p_derived + offsetof(Derived, b));

    printf("=== Двійкова розкладка об'єкта в C ===\n");
    printf("Розмір Derived:  %zu байтів\n", sizeof(Derived));
    printf("Адреса Derived:  %p (зсув 0)\n", (void*)p_derived);
    printf("Адреса BaseA*:   %p (зсув %zu B)\n", (void*)p_a, offsetof(Derived, a));
    printf("Адреса BaseB*:   %p (зсув +%zu B)\n", (void*)p_b, offsetof(Derived, b));
    printf("Зсув d_val:      %zu B\n", offsetof(Derived, d_val));

    /* Виклик методів через поліморфні покажчики */
    p_a->vptr_A->funcA(p_a);
    p_b->vptr_B->funcB(p_b);

    return 0;
}
