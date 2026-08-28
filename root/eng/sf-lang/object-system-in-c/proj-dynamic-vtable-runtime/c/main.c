#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define PI 3.14159265358979323846

/* ── 1. Базовий клас: Object та ObjectClass ───────────────────────────────── */

typedef struct Object Object;
typedef struct ObjectClass ObjectClass;

struct ObjectClass {
    uint32_t type_id;
    const char *type_name;
    ObjectClass *parent_class;
    size_t instance_size;
    
    /* Віртуальні методи */
    void (*dispose)(Object *self);
    void (*to_string)(Object *self, char *buffer, size_t buf_len);
};

struct Object {
    ObjectClass *klass;       /* Вказівник на таблицю методів (зсув 0) */
    int ref_count;            /* Лічильник посилань */
};

/* Макрос безпечного приведення типу з перевіркою часу виконання */
#define OBJECT_CAST(obj, target_type_id, TargetType) \
    ((object_is_a((Object*)(obj), (target_type_id))) ? ((TargetType*)(obj)) : NULL)

bool object_is_a(Object *obj, uint32_t target_type_id) {
    if (!obj || !obj->klass) return false;
    for (ObjectClass *k = obj->klass; k != NULL; k = k->parent_class) {
        if (k->type_id == target_type_id) return true;
    }
    return false;
}

Object* object_ref(Object *self) {
    if (self) self->ref_count++;
    return self;
}

void object_unref(Object *self) {
    if (!self) return;
    if (--self->ref_count <= 0) {
        if (self->klass && self->klass->dispose) {
            self->klass->dispose(self);
        }
        free(self);
    }
}

void object_base_dispose(Object *self) {
    /* Базовий деструктор: очищення спільних ресурсів Object */
    (void)self;
}

void object_base_to_string(Object *self, char *buffer, size_t buf_len) {
    snprintf(buffer, buf_len, "<%s at %p, refcount=%d>", 
             self->klass->type_name, (void*)self, self->ref_count);
}

/* ── 2. Проміжний клас: Shape та ShapeClass ───────────────────────────────── */

#define TYPE_OBJECT 0x1000
#define TYPE_SHAPE  0x2000
#define TYPE_CIRCLE 0x3000

typedef struct Shape Shape;
typedef struct ShapeClass ShapeClass;

struct ShapeClass {
    ObjectClass base_class;   /* Спадкування класу vtable (зсув 0) */
    
    /* Нові віртуальні методи фігури */
    double (*area)(Shape *self);
    double (*perimeter)(Shape *self);
};

struct Shape {
    Object base;              /* Базовий під-об'єкт Object (зсув 0) */
    const char *color;        /* Власне поле фігури */
};

/* ── 3. Конкретний клас: Circle ───────────────────────────────────────────── */

typedef struct {
    Shape base;               /* Базовий під-об'єкт Shape (зсув 0) */
    double radius;            /* Власне поле кола */
} Circle;

typedef struct {
    ShapeClass base_class;    /* Базовий клас ShapeClass (зсув 0) */
} CircleClass;

double circle_area(Shape *self) {
    Circle *c = (Circle*)self;
    return PI * c->radius * c->radius;
}

double circle_perimeter(Shape *self) {
    Circle *c = (Circle*)self;
    return 2.0 * PI * c->radius;
}

void circle_to_string(Object *self, char *buffer, size_t buf_len) {
    Circle *c = (Circle*)self;
    snprintf(buffer, buf_len, "Circle(color=%s, radius=%.2f, area=%.2f)", 
             c->base.color, c->radius, circle_area((Shape*)c));
}

void circle_dispose(Object *self) {
    /* Очищення власних ресурсів кола перед викликом деструктора предка */
    Circle *c = (Circle*)self;
    (void)c;
    
    /* Ланцюговий виклик деструктора батьківського класу */
    ObjectClass *parent = self->klass->parent_class;
    if (parent && parent->dispose) {
        parent->dispose(self);
    }
}

/* Глобальні таблиці класів (синглтони vtable) */
static ObjectClass g_object_class = {
    .type_id = TYPE_OBJECT,
    .type_name = "Object",
    .parent_class = NULL,
    .instance_size = sizeof(Object),
    .dispose = object_base_dispose,
    .to_string = object_base_to_string
};

static ShapeClass g_shape_class;
static CircleClass g_circle_class;

void init_type_system(void) {
    /* Ініціалізація ShapeClass */
    g_shape_class.base_class.type_id = TYPE_SHAPE;
    g_shape_class.base_class.type_name = "Shape";
    g_shape_class.base_class.parent_class = &g_object_class;
    g_shape_class.base_class.instance_size = sizeof(Shape);
    g_shape_class.base_class.dispose = object_base_dispose;
    g_shape_class.base_class.to_string = object_base_to_string;
    g_shape_class.area = NULL;
    g_shape_class.perimeter = NULL;

    /* Ініціалізація CircleClass з перевизначенням методів */
    g_circle_class.base_class.base_class.type_id = TYPE_CIRCLE;
    g_circle_class.base_class.base_class.type_name = "Circle";
    g_circle_class.base_class.base_class.parent_class = (ObjectClass*)&g_shape_class;
    g_circle_class.base_class.base_class.instance_size = sizeof(Circle);
    g_circle_class.base_class.base_class.dispose = circle_dispose;
    g_circle_class.base_class.base_class.to_string = circle_to_string;
    g_circle_class.base_class.area = circle_area;
    g_circle_class.base_class.perimeter = circle_perimeter;
}

Circle* circle_new(const char *color, double radius) {
    Circle *c = (Circle*)calloc(1, sizeof(Circle));
    if (!c) return NULL;
    
    /* Зв'язування з vtable та встановлення початкових полів */
    c->base.base.klass = (ObjectClass*)&g_circle_class;
    c->base.base.ref_count = 1;
    c->base.color = color;
    c->radius = radius;
    return c;
}

/* ── 4. Демонстрація поліморфного використання ────────────────────────────── */

int main(void) {
    init_type_system();

    Circle *c = circle_new("Red", 5.0);
    Object *obj = (Object*)c;

    /* Поліморфний виклик to_string через vtable */
    char desc[128];
    obj->klass->to_string(obj, desc, sizeof(desc));
    printf("Опис об'єкта: %s\n", desc);

    /* Безпечне динамічне приведення вниз (downcast) */
    Shape *shape = OBJECT_CAST(obj, TYPE_SHAPE, Shape);
    if (shape) {
        ShapeClass *s_klass = (ShapeClass*)shape->base.klass;
        printf("Площа фігури: %.2f\n", s_klass->area(shape));
        printf("Периметр фігури: %.2f\n", s_klass->perimeter(shape));
    }

    /* Підрахунок посилань */
    object_ref(obj);
    printf("Після object_ref(): ref_count = %d\n", obj->ref_count);
    object_unref(obj);
    printf("Після першого object_unref(): ref_count = %d\n", obj->ref_count);
    
    /* Фінальне звільнення */
    object_unref(obj);
    return 0;
}
