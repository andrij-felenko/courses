# ⚙️ Ручна реалізація динамічного зв'язування: vtable, itable та fat pointers на C та C++

Усі високорівневі конструкції об'єктно-орієнтованих мов — ключове слово `virtual`, абстрактні класи, інтерфейси Java, трейт-об'єкти Rust чи протоколи Swift — під час компіляції транслюються у звичайні структури даних із покажчиками на функції та непрямі інструкції переходу процесора. Якщо реалізувати ці механізми вручну на низькому рівні, стає очевидним кожен байт накладних витрат: де саме лежить таблиця методів, скільки звернень до пам'яті вимагає виклик і чому множинне спадкування потребує коригування покажчика `this`.

У цьому практичному дослідженні ми збудуємо три фундаментальні архітектурні моделі динамічного зв'язування «з нуля» мовами C та ідіоматичним C++:
1. Класична віртуальна таблиця з одинарним спадкуванням (модель C++ / Java).
2. Множинне інтерфейсне спадкування з перехідниками зміщення покажчика (Adjustor Thunks).
3. Розв'язана диспетчеризація через жирні покажчики (модель Rust `&dyn Trait` / Go `iface`).

## 1. КЛАСИЧНА ВІРТУАЛЬНА ТАБЛИЦЯ (VTABLE)

У моделі віртуальних таблиць одинарного спадкування кожен екземпляр класу містить приховане перше поле — покажчик `vptr`. Цей покажчик ініціалізується під час конструювання об'єкта і веде на глобальну константну таблицю адрес функцій `VTable`, розташовану у сегменті пам'яті `.rodata` (доступному лише для читання).

### Механізм роботи та макет пам'яті

Коли створюється об'єкт `Circle`, у пам'яті виділяється блок, де перші 8 байтів відведено під `vptr`, а наступні байти — під корисні поля даних (`radius`). Усі об'єкти типу `Circle` мають однакове значення `vptr`, яке вказує на одну спільну статичну структуру `CIRCLE_VTABLE`.

Поліморфна функція `compute_total_area` приймає масив покажчиків на абстрактний базовий тип `Shape`. Вона не має жодного уявлення про те, які саме конкретні геометричні фігури лежать у пам'яті. Для кожної фігури вона зчитує `vptr`, знаходить адресу потрібного методу за фіксованим індексом слота і здійснює непрямий перехід, передаючи покажчик на сам об'єкт як перший аргумент `self`.

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <numbers>
#include <span>

/* Контракт таблиці віртуальних функцій */
struct ShapeVTable {
    void (*draw)(const void* self) noexcept;
    double (*area)(const void* self) noexcept;
};

/* Базова структура з vptr у нульовому зміщенні */
struct Shape {
    const ShapeVTable* vptr{nullptr};

    void draw() const noexcept {
        vptr->draw(this);
    }

    [[nodiscard]] double area() const noexcept {
        return vptr->area(this);
    }
};

/* Конкретний тип Коло */
struct Circle {
    Shape base;
    double radius{0.0};

    explicit Circle(double r) noexcept : radius(r) {
        static constexpr ShapeVTable vtable{
            .draw = [](const void* self) noexcept {
                const auto* c = static_cast<const Circle*>(self);
                (void)c;
            },
            .area = [](const void* self) noexcept -> double {
                const auto* c = static_cast<const Circle*>(self);
                return std::numbers::pi * c->radius * c->radius;
            }
        };
        base.vptr = &vtable;
    }
};

/* Поліморфна функція, що працює з діапазоном покажчиків */
[[nodiscard]] double compute_total_area(std::span<const Shape* const> shapes) noexcept {
    double total = 0.0;
    for (const auto* s : shapes) {
        total += s->area();
    }
    return total;
}
```
:::

### Аналіз накладних витрат одинарної vtable

Ця реалізація показує точну ціну абстракції:
1. **Накладні витрати пам'яті:** кожен об'єкт збільшується на 8 байтів (розмір `vptr` на 64-бітній платформі). Навіть якщо клас містить лише одне 4-байтне число `int`, через вирівнювання пам'яті (alignment) весь об'єкт займе 16 байтів.
2. **Накладні витрати часу:** на один виклик припадає два звернення до пам'яті (читання `vptr` з об'єкта, потім читання адреси функції з таблиці) плюс один непрямий перехід. За умови прогрітого кешу L1 це коштує близько 2–4 тактів процесора.

## 2. МНОЖИННЕ СПАДКУВАННЯ ТА ADJUSTOR THUNK

Коли клас реалізує кілька незалежних інтерфейсів, компілятор розміщує в пам'яті кілька таблиць `vptr`. При приведенні покажчика на об'єкт до вторинного інтерфейсу адреса зміщується вперед на зміщення поля цього інтерфейсу в структурі. 

### Чому виникає потреба в перехіднику (Thunk)

Уявімо складений графічний елемент `Button`, який одночасно реалізує два інтерфейси: `IDrawable` (для відображення на екрані) та `ISerializable` (для збереження стану у двійковий потік).

У пам'яті екземпляр `Button` компонується так:
```
Байт 0..7:   vptr для IDrawable
Байт 8..15:  vptr для ISerializable
Байт 16..23: width та height
```

Якщо функція збереження очікує покажчик `ISerializable*`, клієнт передає їй адресу, зміщену на `+8` байтів відносно початку `Button`. Коли клієнт робить виклик `serializable->vptr->serialize(serializable, buffer, len)`, у якості аргументу `self` передається адреса підвиду `ISerializable`, тобто `(адреса Button + 8)`.

Але метод `button_real_serialize(Button *b, ...)` очікує у ролі першого аргументу покажчик на *початок усього об'єкта `Button`*! Якщо він спробує прочитати поле `b->width` за зміщенням `+16` від переданого `self`, він насправді прочитає пам'ять за зміщенням `+24`, тобто сміття або чужі дані.

Щоб відновити правильну адресу `this`, у віртуальну таблицю інтерфейсу `ISerializable` записується адреса **Adjustor Thunk** — допоміжної функції-перехідника, яка віднімає 8 байтів від отриманого `self` і лише після цього передає керування справжньому методу.

:::tabs
```c
#include <stddef.h>
#include <stdint.h>

/* Інтерфейс 1: Малювання */
typedef struct IDrawableVTable {
    void (*draw)(void *self);
} IDrawableVTable;

typedef struct IDrawable {
    const IDrawableVTable *vptr;
} IDrawable;

/* Інтерфейс 2: Серіалізація */
typedef struct ISerializableVTable {
    void (*serialize)(void *self, uint8_t *buffer, size_t max_len);
} ISerializableVTable;

typedef struct ISerializable {
    const ISerializableVTable *vptr;
} ISerializable;

/* Похідний клас Button реалізує обидва інтерфейси */
typedef struct Button {
    IDrawable drawable_base;         /* зміщення 0 */
    ISerializable serializable_base; /* зміщення sizeof(IDrawable) = 8 байтів */
    int width;
    int height;
} Button;

/* Цільові методи Button, що очікують покажчик саме на Button* */
static void button_real_draw(Button *b) {
    (void)b;
}

static void button_real_serialize(Button *b, uint8_t *buf, size_t len) {
    (void)b; (void)buf; (void)len;
}

/* Thunk для IDrawable (зміщення 0, коригування не потрібне) */
static void thunk_drawable_draw(void *self) {
    Button *b = (Button *)self;
    button_real_draw(b);
}

/* Thunk для ISerializable: self вказує на serializable_base!
   Потрібно скоригувати self назад на початок Button */
static void thunk_serializable_serialize(void *self, uint8_t *buf, size_t len) {
    uint8_t *ptr = (uint8_t *)self;
    /* Віднімаємо зміщення поля serializable_base відносно Button */
    Button *b = (Button *)(ptr - offsetof(Button, serializable_base));
    button_real_serialize(b, buf, len);
}

static const IDrawableVTable BUTTON_DRAWABLE_VTBL = {
    .draw = thunk_drawable_draw
};

static const ISerializableVTable BUTTON_SERIALIZABLE_VTBL = {
    .serialize = thunk_serializable_serialize
};

static void button_init(Button *b, int w, int h) {
    b->drawable_base.vptr = &BUTTON_DRAWABLE_VTBL;
    b->serializable_base.vptr = &BUTTON_SERIALIZABLE_VTBL;
    b->width = w;
    b->height = h;
}
```
```cpp
#include <cstddef>
#include <cstdint>
#include <span>

struct IDrawableVTable {
    void (*draw)(void* self) noexcept;
};

struct IDrawable {
    const IDrawableVTable* vptr{nullptr};
};

struct ISerializableVTable {
    void (*serialize)(void* self, std::span<uint8_t> out) noexcept;
};

struct ISerializable {
    const ISerializableVTable* vptr{nullptr};
};

/* Складений клас із двома незалежними vptr */
struct Button {
    IDrawable drawable_base;
    ISerializable serializable_base;
    int width{0};
    int height{0};

    void actual_draw() noexcept {
        /* Логіка малювання кнопки */
    }

    void actual_serialize(std::span<uint8_t> out) noexcept {
        /* Логіка серіалізації кнопки */
        (void)out;
    }

    Button(int w, int h) noexcept : width(w), height(h) {
        static constexpr IDrawableVTable draw_vtbl{
            .draw = [](void* self) noexcept {
                auto* b = static_cast<Button*>(self);
                b->actual_draw();
            }
        };

        static constexpr ISerializableVTable ser_vtbl{
            .serialize = [](void* self, std::span<uint8_t> out) noexcept {
                auto* bytes = static_cast<uint8_t*>(self);
                auto* b = reinterpret_cast<Button*>(bytes - offsetof(Button, serializable_base));
                b->actual_serialize(out);
            }
        };

        drawable_base.vptr = &draw_vtbl;
        serializable_base.vptr = &ser_vtbl;
    }
};
```
:::

На рівні машинного коду компілятори GCC та Clang реалізують такі thunk-перехідники як хвостовий стрибок (tail call) без виділення стекового кадру: `sub $8, %rdi; jmp Button::serialize`. Це зводить накладні витрати множинного спадкування лише до однієї додаткової арифметичної інструкції віднімання.

## 3. РОЗВ'ЯЗАНА ДИСПЕТЧЕРИЗАЦІЯ: FAT POINTERS (RUST-МОДЕЛЬ)

У класичних об'єктно-орієнтованих мовах зв'язок між об'єктом і його таблицею методів є нерозривним: кожен об'єкт несе `vptr` у своєму заголовку, навіть якщо поліморфізм для конкретного екземпляра ніколи не знадобиться.

Модель **жирних покажчиків** (англ. *fat pointers*, реалізована у Rust як `&dyn Trait` та в Go як інтерфейсні змінні `iface`) розриває цей зв'язок.

### Архітектура жирного покажчика

Сам об'єкт залишається чистою, мономорфною структурою без жодного накладного байта в пам'яті. Коли об'єкт передається у функцію, яка вимагає поліморфного інтерфейсу, на стеку створюється складений покажчик розміром у два машинних слова (16 байтів):
1. `data_ptr`: чиста адреса структури даних об'єкта.
2. `vtable_ptr`: адреса статичної таблиці методів для цієї пари «(тип, інтерфейс)».

:::tabs
```c
#include <stdio.h>
#include <stdint.h>

/* Трейт Логування: таблиця функцій */
typedef struct LogTraitVTable {
    void (*log_info)(const void *data);
} LogTraitVTable;

/* Жирний покажчик (Fat Pointer) розміром 16 байтів */
typedef struct DynLogger {
    const void *data_ptr;              /* 8 байтів: адреса сирих даних */
    const LogTraitVTable *vtable_ptr;  /* 8 байтів: адреса трейт-таблиці */
} DynLogger;

/* Чиста структура без vptr всередині: розмір рівно 8 байтів */
typedef struct SensorData {
    int32_t temperature;
    int32_t humidity;
} SensorData;

static void sensor_log_impl(const void *data) {
    const SensorData *s = (const SensorData *)data;
    /* У реальній системі тут форматований запис у лог */
    (void)s;
}

static const LogTraitVTable SENSOR_LOG_VTABLE = {
    .log_info = sensor_log_impl
};

/* Створення жирного покажчика на стеку */
static DynLogger make_sensor_logger(const SensorData *s) {
    DynLogger dyn = {
        .data_ptr = s,
        .vtable_ptr = &SENSOR_LOG_VTABLE
    };
    return dyn;
}

/* Приймач жирного покажчика */
static void process_log(DynLogger logger) {
    /* Прямий виклик через передану таблицю без опитування пам'яті об'єкта */
    logger.vtable_ptr->log_info(logger.data_ptr);
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <concepts>

/* Опис трейт-контракту */
template <typename TraitVTable>
struct DynRef {
    const void* data_ptr{nullptr};
    const TraitVTable* vtable_ptr{nullptr};
};

struct LoggerVTable {
    void (*log_msg)(const void* data) noexcept;
};

/* Чистий тип без спадкування та без vptr */
struct TemperatureSensor {
    int32_t celsius{0};
    uint32_t sensor_id{0};
};

/* Будівник жирного покажчика для типу TemperatureSensor */
class LoggerTrait {
public:
    template <typename T>
    [[nodiscard]] static DynRef<LoggerVTable> create(const T& obj) noexcept {
        static constexpr LoggerVTable vtbl{
            .log_msg = [](const void* data) noexcept {
                const auto* val = static_cast<const T*>(data);
                (void)val;
            }
        };

        return DynRef<LoggerVTable>{
            .data_ptr = &obj,
            .vtable_ptr = &vtbl
        };
    }
};

/* Функція, що приймає знеособлений жирний покажчик */
void execute_log(DynRef<LoggerVTable> dyn) noexcept {
    dyn.vtable_ptr->log_msg(dyn.data_ptr);
}
```
:::

### Чому fat pointers перемагають у системному програмуванні

Модель жирних покажчиків дає три вирішальні інженерні переваги:
1. **Нульові накладні витрати на мономорфний код:** якщо ви зберігаєте мільйон структур `SensorData` у масиві, вам не потрібно витрачати 8 МБ пам'яті на мільйон однакових `vptr`. Дані лежать щільно в кеш-лініях, що критично для високої продуктивності та Data-Oriented Design (DOD).
2. **Ретроактивна реалізація інтерфейсів:** ви можете реалізувати інтерфейс `Logger` для стандартного типу `int32_t` або для сторонньої структури з закритої бібліотеки, не змінюючи її розмір і макет у пам'яті.
3. **Ефективність виклику:** процесор завантажує `vtable_ptr` безпосередньо з аргументів виклику (які вже лежать у реєстрах), уникаючи зайвого звернення до пам'яті об'єкта для читання `vptr`.

## 4. ПОРІВНЯННЯ НАКЛАДНИХ ВИТРАТ ТА ІНЖЕНЕРНИЙ ВИСНОВОК

Зіставимо всі три низькорівневі моделі в єдиній таблиці:

| Критерій | Вбудований vptr (C++) | Множинне спадкування (C++) | Жирний покажчик (Rust / Go) |
| :--- | :--- | :--- | :--- |
| **Розмір покажчика** | 8 байтів | 8 байтів | 16 байтів (два машинних слова) |
| **Розмір об'єкта** | +8 байтів на `vptr` | +8 байтів на кожен базовий інтерфейс | 0 байтів (чисті дані) |
| **Кількість розіменувань** | 2 (читання `vptr` + перехід) | 2 + стрибок у thunk | 1 (`vtable_ptr` уже в регістрі) |
| **Підтримка сторонніх типів** | Неможлива без обгортки | Неможлива без обгортки | Вільна (через окремі таблиці) |
| **Вплив на кеш процесора** | Об'єкти займають більше місця | Складний макет, фрагментація | Максимальна щільність даних |

Вибір архітектури динамічного зв'язування визначає продуктивність усієї системи:
- Для закритих ієрархій із високою частотою викликів одного методу найкраще підходить класичний vtable або мономорфізація через шаблони.
- Для відкритих систем із високими вимогами до щільності пам'яті та модульності неперевершеною є модель жирних покажчиків.
