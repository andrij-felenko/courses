# ⚙️ Реалізація модульної об'єктної системи з vtable та підрахунком посилань

Для глибокого розуміння промислових об'єктних моделей корисно побудувати мінімальну, але повнофункціональну об'єктну систему з нуля. Головна інженерна задача полягає в тому, щоб забезпечити три базові стовпи об'єктноорієнтованого програмування: інкапсуляцію даних, одиничне спадкування з гарантією сумісності розкладки пам'яті та поліморфну диспетчеризацію методів через таблиці покажчиків (vtable) разом із детермінованим керуванням пам'яттю на основі підрахунку посилань.

Нижче наведено повністю робочий і самодостатній приклад ієрархії: базовий об'єкт `Object` (керує життєвим циклом та рядковим представленням), абстрактна фігура `Shape` (додає контракт обчислення площі) та конкретний клас `Circle`.

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <format>
#include <numbers>
#include <vector>

/* ── 1. Базовий клас Object з ідіоматичним C++ поліморфізмом ──────────────── */

class Object : public std::enable_shared_from_this<Object> {
public:
    virtual ~Object() = default;

    [[nodiscard]] virtual std::string to_string() const {
        return std::format("<Object at {}, use_count={}>", 
                           static_cast<const void*>(this), 
                           shared_from_this().use_count());
    }
};

/* ── 2. Проміжний абстрактний клас Shape ─────────────────────────────────── */

class Shape : public Object {
public:
    explicit Shape(std::string color) : m_color(std::move(color)) {}
    
    [[nodiscard]] virtual double area() const = 0;
    [[nodiscard]] virtual double perimeter() const = 0;
    [[nodiscard]] const std::string& color() const noexcept { return m_color; }

private:
    std::string m_color;
};

/* ── 3. Конкретний клас Circle ───────────────────────────────────────────── */

class Circle final : public Shape {
public:
    Circle(std::string color, double radius)
        : Shape(std::move(color)), m_radius(radius) {}

    [[nodiscard]] double area() const override {
        return std::numbers::pi * m_radius * m_radius;
    }

    [[nodiscard]] double perimeter() const override {
        return 2.0 * std::numbers::pi * m_radius;
    }

    [[nodiscard]] std::string to_string() const override {
        return std::format("Circle(color={}, radius={:.2f}, area={:.2f})", 
                           color(), m_radius, area());
    }

    [[nodiscard]] double radius() const noexcept { return m_radius; }

private:
    double m_radius;
};

/* ── 4. Демонстрація поліморфного використання ────────────────────────────── */

int main() {
    // std::make_shared автоматично створює блок керування з атомарним ref_count
    std::shared_ptr<Object> obj = std::make_shared<Circle>("Red", 5.0);

    // Поліморфний виклик через vtable компілятора
    std::cout << "Опис об'єкта: " << obj->to_string() << '\n';

    // Безпечне приведення вниз через dynamic_pointer_cast (RTTI)
    if (auto shape = std::dynamic_pointer_cast<Shape>(obj)) {
        std::cout << "Площа фігури: " << shape->area() << '\n';
        std::cout << "Периметр фігури: " << shape->perimeter() << '\n';
    }

    std::cout << "Поточний use_count: " << obj.use_count() << '\n';

    // Копіювання shared_ptr збільшує лічильник атомарно
    {
        std::shared_ptr<Object> alias = obj;
        std::cout << "У вкладеному блоці use_count: " << obj.use_count() << '\n';
    }
    std::cout << "Після виходу з блоку use_count: " << obj.use_count() << '\n';

    // Автоматичне викликання віртуального деструктора при виході з main
    return 0;
}
```
:::

## Покроковий розбір архітектури та керування пам'яттю

Реалізована система відтворює ключові компоненти промислових об'єктних рантаймів без залучення зовнішніх бібліотек. Розглянемо детально кожен рівень взаємодії.

### 1. Префіксне вкладення базових структур та нульове зміщення
У структурі `Circle` базовий тип `Shape` розміщено найпершим полем за значенням (`Shape base`), а всередині `Shape` аналогічно найпершим полем вбудовано `Object base`. Першим полем структури `Object` є покажчик на таблицю методів `klass`.

За стандартом C11 (§6.7.2.1), адреса структури гарантовано збігається з адресою її першого поля. Це забезпечує фундаментальну рівність покажчиків у пам'яті:

```
(uintptr_t)c == (uintptr_t)&(c->base) == (uintptr_t)&(c->base.base) == (uintptr_t)&(c->base.base.klass)
```

Завдяки цьому операція приведення типу `(Object*)circle` або `(Shape*)circle` не генерує жодних інструкцій зміщення адреси процесором. Зсув `Δ = 0` байтів робить приведення вгору абсолютно безкоштовним під час виконання програми.

### 2. Ієрархія таблиць класів та ланцюжкове перевизначення методів
Кожна таблиця класу існує як глобальний синглтон (`g_circle_class`). При створенні нащадка його таблиця методів `CircleClass` містить у собі таблицю предка `ShapeClass` за нульовим зміщенням.

Якщо похідний клас перевизначає віртуальний метод (наприклад, `to_string`), покажчик на власну функцію `circle_to_string` записується безпосередньо у відповідний слот vtable. Якщо метод не перевизначено, у слоті залишається адреса функції базового класу (`object_base_to_string`).

Під час деструкції об'єкта похідний клас зобов'язаний самостійно забезпечити виклик деструктора батьківського класу. Для цього використовується поле `parent_class`:

:::tabs
```c
/* Ручний виклик деструктора базового класу в C */
ObjectClass *parent = self->klass->parent_class;
if (parent && parent->dispose) {
    parent->dispose(self);
}
```
```cpp
// У C++ виклик деструктора базового класу генерується компілятором автоматично
// Circle::~Circle() автоматично викликає Shape::~Shape(), а той — Object::~Object()
```
:::

Якщо розробник забуде викликати батьківський `dispose`, ресурси предка (відкриті сокети, дескриптори або підлеглі буфери) будуть втрачені. У C++ цей ланцюжок деструкції повністю контролюється компілятором і виконується у зворотному порядку спадкування автоматично.

### 3. Динамічна типізація та захист від небезпечного приведення
Оскільки в C немає вбудованої інформації про типи часу виконання (RTTI), спроба привести покажчик на довільний `Object*` до типу `Circle*` через звичайний C-cast `(Circle*)obj` може призвести до зчитування сміття, якщо переданий об'єкт насправді є іншим підтипом.

Макрос `OBJECT_CAST` виконує динамічну валідацію: функція `object_is_a` проходить по ланцюжку покажчиків `parent_class`, порівнюючи числові ідентифікатори `type_id`. Якщо цільовий тип знайдено в дереві предків, макрос повертає приведену адресу; якщо ні — повертається `NULL`. Це усуває ризик некоректної інтерпретації пам'яті.

### 4. Апаратна вартість диспетчеризації та оптимізація кешу
У машинному коді непрямий виклик `obj->klass->to_string(obj, ...)` транслюється в асемблерну послідовність із двох читань пам'яті та однієї інструкції непрямого переходу:

```
movq (%rdi), %rax        ; %rax = obj->klass (перше розіменування вказівника на vtable)
movq 40(%rax), %r11      ; %r11 = klass->to_string (друге розіменування адреси функції)
call *%r11               ; Непрямий перехід на адресу цільової функції
```

Перше читання тягне заголовок об'єкта в кеш L1d. Оскільки таблиці класів `ObjectClass` є статичними синглтонами, вони практично завжди залишаються прогрітими в кеші процесора. Проте непрямий виклик `call *%r11` навантажує блок передбачення переходів (англ. *Branch Target Buffer, BTB*). Якщо поліморфний цикл обробляє різнорідні об'єкти (коло, прямокутник, трикутник), передбачення цілі переходу скидається, що призводить до штрафу конвеєра в 12–20 тактів процесора на кожен виклик.

У нативному C++ компілятор під час оптимізації (LTO, профілювання PGO або за наявності ключового слова `final`) здатен виконувати девіртуалізацію (англ. *devirtualization*): замінювати непрямий `call *%r11` на прямий перехід `call circle_to_string` та виконувати наступне вбудовування (inlining) функції в тіло циклу. Ручна об'єктна система в C не дає компілятору інформації про незмінність vtable, тому оптимізатор змушений завжди генерувати повний непрямий виклик.

### 5. Правила еволюції ABI та розширення таблиць vtable
При поширенні об'єктної системи у вигляді динамічної бібліотеки (`.so` або `.dll`) критично важливим є збереження двійкової сумісності (ABI). 

Якщо в новій версії бібліотеки до структури `ShapeClass` додається новий віртуальний метод (наприклад, `double (*bounding_box)(Shape *self)`), його покажчик **зобов'язаний додаватися строго в кінець структури**. Якщо вставити нове поле всередину або на початок структури, зміщення всіх наступних покажчиків функцій у пам'яті зміняться. Клієнтська програма, скомпільована зі старою версією заголовного файлу, при спробі викликати `perimeter()` прочитає адресу нового методу `bounding_box()`, передасть некоректні параметри та аварійно завершиться. Дописування нових методів у кінець vtable гарантує збереження чинних зміщень для старих клієнтів.

## Пастки проектування об'єктних моделей у C

При розробці об'єктних систем у мовах без прямої підтримки компілятора виникають специфічні підводні камені:

1. **Зрізання об'єктів при передачі за значенням (Object Slicing):**
   Усі операції з об'єктами повинні виконуватися виключно через покажчики (`Object*`). Якщо випадково спробувати скопіювати об'єкт через присвоєння значень структур `*shape_ptr = *(Shape*)circle_ptr`, скопійовано буде лише базовий зріз пам'яті, а специфічні поля `Circle` (наприклад, `radius`) будуть відкинуті.
2. **Висячі покажчики на vtable (Dangling Vptr):**
   Якщо екземпляр створено на стеку, а не виділено динамічно в купі через `calloc()`, передача його в асинхронні колбеки або виклик `object_unref()` спричинить спробу виклику `free()` для адреси стека, що призведе до аварійного завершення програми.
3. **Циклічні посилання та витоки ресурсів:**
   Простий лічильник посилань `ref_count` не здатний самостійно виявити взаємне утримання двох об'єктів у циклічному графі. Для запобігання вічним витокам пам'яті у складних графах вимагається впровадження слабких посилань (weak references) або протоколу двоетапного знищення `dispose`/`finalize`, аналогічно системі GObject.
