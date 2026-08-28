#include <stdio.h>
#include <math.h>

/* Інтерфейс базового класу у формі таблиці покажчиків */
typedef struct ShapeVTable {
    void (*draw)(const void *self);
    double (*area)(const void *self);
} ShapeVTable;

/* Базовий тип містить лише vptr як перше поле */
typedef struct Shape {
    const ShapeVTable *vptr;
} Shape;

/* Похідний тип: Коло */
typedef struct Circle {
    Shape base;        /* vptr стоїть за зміщенням 0 */
    double radius;
} Circle;

/* Реалізації методів для Кола */
static void circle_draw(const void *self) {
    const Circle *c = (const Circle *)self;
    /* У реальному коді тут малювання кола радіуса c->radius */
    (void)c;
}

static double circle_area(const void *self) {
    const Circle *c = (const Circle *)self;
    return 3.141592653589793 * c->radius * c->radius;
}

/* Статична константна таблиця методів для Circle */
static const ShapeVTable CIRCLE_VTABLE = {
    .draw = circle_draw,
    .area = circle_area
};

/* Конструктор кола */
static void circle_init(Circle *c, double r) {
    c->base.vptr = &CIRCLE_VTABLE;
    c->radius = r;
}

/* Поліморфна функція: не знає конкретного типу об'єкта */
static double compute_total_area(const Shape *const *shapes, size_t count) {
    double total = 0.0;
    for (size_t i = 0; i < count; ++i) {
        const Shape *s = shapes[i];
        /* Непрямий виклик через vtable: 
           1. Читаємо vptr: s->vptr
           2. Беремо адресу методу: vptr->area
           3. Передаємо s як self */
        total += s->vptr->area(s);
    }
    return total;
}
