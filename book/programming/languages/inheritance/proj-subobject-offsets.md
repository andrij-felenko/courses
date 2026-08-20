# ⚙️ Дослідження бінарного розкладання та зсувів покажчиків у пам'яті

Щоб побачити, як компілятор транслює високорівневі абстракції спадкування в машинний код, процесорні інструкції та фізичні байти пам'яті, напишемо комплексну діагностичну програму. Ми дослідимо внутрішні механізми об'єктної моделі на трьох рівнях:
1. **Арифметика зміщення покажчиків (Pointer Adjustment):** як саме змінюється чисельне значення адреси при приведенні нащадка до другого й наступних базових класів, чому наївне приведення через `reinterpret_cast` неминуче руйнує пам'ять, і як компілятор генерує інструкції зміщення регістрів `this`.
2. **Захист від зсуву нульового вказівника (`nullptr`):** як компілятор запобігає виникненню фальшивих ненульових адрес при зміщенні баз у випадку нульових покажчиків.
3. **Метадані віртуальних баз у таблиці `vtable`:** як прочитати зсуви `offset-to-top` та зміщення до спільної віртуальної бази безпосередньо з від'ємних слотів віртуальної таблиці згідно зі специфікацією Itanium C++ ABI.

## Експеримент 1: Множинне спадкування та Pointer Adjustment

Коли об'єкт успадковує два незалежні класи з віртуальними функціями, компілятор створює всередині нього два окремі під-об'єкти. Кожен із них отримує власне службове поле `vptr` для забезпечення коректної роботи віртуальних викликів через поліморфні інтерфейси.

У наступному прикладі ми реалізуємо цю модель двома мовами: на чистому C (де вся механіка розкладки, зсувів та thunk-функцій моделюється вручну через вкладені структури, вказівники та макрос `offsetof`) та на C++ (де компілятор автоматично керує зміщеннями під час приведення типів).

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <iomanip>
#include <cstdint>
#include <cstddef>

class BaseA {
public:
    virtual void funcA() { std::cout << "BaseA::funcA\n"; }
    int a_val{100};
};

class BaseB {
public:
    virtual void funcB() { std::cout << "BaseB::funcB\n"; }
    int b_val{200};
};

class Derived : public BaseA, public BaseB {
public:
    void funcA() override { 
        std::cout << "Derived::funcA виконано (d_val = " << d_val << ")\n"; 
    }
    void funcB() override { 
        std::cout << "Derived::funcB виконано (d_val = " << d_val << ")\n"; 
    }
    int d_val{300};
};

int main() {
    Derived obj;
    Derived* p_derived = &obj;

    // Upcast: компілятор неявно генерує арифметику вказівників
    BaseA* p_a = static_cast<BaseA*>(p_derived);
    BaseB* p_b = static_cast<BaseB*>(p_derived);

    std::cout << "=== Двійкова розкладка об'єкта в C++ ===\n";
    std::cout << "Розмір Derived: " << sizeof(Derived) << " байтів\n";
    std::cout << "Адреса Derived: " << static_cast<void*>(p_derived) << "\n";
    std::cout << "Адреса BaseA*:  " << static_cast<void*>(p_a) 
              << " (Δ = " << reinterpret_cast<uintptr_t>(p_a) - reinterpret_cast<uintptr_t>(p_derived) << " B)\n";
    std::cout << "Адреса BaseB*:  " << static_cast<void*>(p_b) 
              << " (Δ = +" << reinterpret_cast<uintptr_t>(p_b) - reinterpret_cast<uintptr_t>(p_derived) << " B)\n";

    // Порівняння приведень типів
    BaseB* bad_b = reinterpret_cast<BaseB*>(p_derived);
    std::cout << "\n=== Порівняння безпеки кастингів ===\n";
    std::cout << "static_cast<BaseB*>:      читає b_val = " << p_b->b_val << " (коректно)\n";
    std::cout << "reinterpret_cast<BaseB*>: читає сміття замість b_val = " << bad_b->b_val << " (помилка зсуву!)\n";

    // Виклики віртуальних методів
    p_a->funcA();
    p_b->funcB(); // Виклик через secondary vtable з автоматичним thunk

    return 0;
}
```
:::

### Результати та аналіз пам'яті

Після компіляції програми під 64-бітну архітектуру x86-64 (наприклад, за допомогою GCC або Clang з прапорцем `-O2`) у консоль виводиться точна карта зміщень:

```
=== Двійкова розкладка об'єкта в C++ ===
Розмір Derived: 40 байтів
Адреса Derived: 0x7ffd9b8a0040
Адреса BaseA*:  0x7ffd9b8a0040 (Δ = 0 B)
Адреса BaseB*:  0x7ffd9b8a0050 (Δ = +16 B)

=== Порівняння безпеки кастингів ===
static_cast<BaseB*>:      читає b_val = 200 (коректно)
reinterpret_cast<BaseB*>: читає сміття замість b_val = 100 (помилка зсуву!)
Derived::funcA виконано (d_val = 300)
Derived::funcB виконано (d_val = 300)
```

Детальний аналіз отриманих байтів:
1. Повний об'єкт `Derived` займає 40 байтів:
   - Байти `0..7`: `vptr` для `BaseA` (вказівник на первинну віртуальну таблицю `Derived`).
   - Байти `8..11`: ціле число `a_val` (значення `100`).
   - Байти `12..15`: 4 байти невидимої набивки (padding), вставлені компілятором для вирівнювання наступного 8-байтного покажчика.
   - Байти `16..23`: `vptr` для `BaseB` (вказівник на вторинну віртуальну таблицю `Derived` для гілки `BaseB`).
   - Байти `24..27`: ціле число `b_val` (значення `200`).
   - Байти `28..31`: 4 байти набивки.
   - Байти `32..35`: ціле число `d_val` (значення `300`).
   - Байти `36..39`: фінальна набивка об'єкта до кратності 8 байтам.
2. Приведення `static_cast<BaseB*>(p_derived)` додало до адреси зміщення `+16` байтів. Коли ми виконали `reinterpret_cast<BaseB*>(p_derived)`, компілятор залишив адресу `0x7ffd9b8a0040` без змін. Внаслідок цього вираз `bad_b->b_val` звернувся за зміщенням `+8` від початку об'єкта і прочитав поле `a_val` (число `100`) замість поля `b_val` (число `200`).

## Аналіз асемблерного коду та thunk-перехідників

Щоб зрозуміти, чому виклик `p_b->funcB()` коректно знаходить поле `d_val`, розглянемо згенерований компілятором машинний код.

Згідно з угодою про виклики System V AMD64 ABI, покажчик `this` передається в регістрі `RDI`.
1. Клієнтський код викликає `p_b->funcB()`, тому в регістр `RDI` завантажується адреса `p_b` (тобто `0x7ffd9b8a0050`).
2. За цією адресою лежить вторинна таблиця `vtable`, де слот методу `funcB` вказує на допоміжну функцію — `non-virtual thunk to Derived::funcB()`.
3. Асемблерний код thunk-перехідника складається лише з двох інструкцій:

```nasm
non-virtual thunk to Derived::funcB():
    sub    rdi, 16                 ; віднімаємо 16 байтів від адреси в RDI (відновлюємо адресу Derived*)
    jmp    Derived::funcB()        ; прямий перехід на тіло методу Derived::funcB
```

Thunk відновлює справжню адресу початку об'єкта `Derived` за один такт процесора без створення додаткового стекового кадру. Після стрибка метод `Derived::funcB` отримує правильний `this` і безпомилково звертається до свого поля `d_val` за фіксованим зміщенням `[rdi + 32]`.

## Експеримент 2: Захист від зсуву нульового покажчика

Особливим крайовим випадком є приведення нульового вказівника. Якщо до нульової адреси `nullptr` просто додати зміщення `+16`, результатом стане фіктивна адреса `0x00000010`. Якщо потім передати такий покажчик у функцію, перевірка `if (ptr != nullptr)` поверне `true`, а перша ж спроба розіменування призведе до аварійного завершення програми (Segmentation Fault).

Компілятор C++ запобігає цій катастрофі генеруванням умовної інструкції:

```cpp
Derived* null_ptr = nullptr;
BaseB* b_from_null = static_cast<BaseB*>(null_ptr);
```

Асемблерний код GCC/Clang транслює це приведення так:

```nasm
    test   rdi, rdi            ; перевіряємо, чи вказівник Derived* дорівнює нулю
    je     .is_null            ; якщо нуль — переходимо до мітки .is_null
    lea    rax, [rdi + 16]     ; якщо ненульовий — додаємо зміщення 16 байтів
    jmp    .done
.is_null:
    xor    eax, eax            ; встановлюємо результуючий покажчик у 0 (nullptr)
.done:
```

Цей механізм гарантує непорушність інваріанта системи типів: приведення `nullptr` до будь-якого базового або похідного типу завжди залишається строгим нулем.

## Динамічне приведення типів: dynamic_cast проти static_cast

Коли тип об'єкта достеменно відомий під час компіляції, `static_cast` виконує зміщення вказівника за фіксованою константою за 1 такт процесора. Проте коли програма володіє поліморфним вказівником `BaseA*` або `BaseB*` і не знає, чи вказує він насправді на `Derived`, потрібне динамічне приведення:

```cpp
BaseB* poly_ptr = get_polymorphic_object();
Derived* d_ptr = dynamic_cast<Derived*>(poly_ptr);
```

Під капотом `dynamic_cast` звертається до рантайм-бібліотеки компілятора (`__dynamic_cast` у `libc++abi` або `libsupc++`). Рантайм виконує таку послідовність дій:
1. Зчитує `vptr` переданого об'єкта та знаходить його таблицю `vtable`.
2. Читає з від'ємного слота `vtable[-2]` зміщення `offset-to-top`, яке вказує, де розташовано початок повного об'єкта.
3. Отримує дескриптор типу `type_info` з `vtable[-1]` і порівнює його з дескриптором цільового типу `Derived`.
4. Якщо тип збігається або є підтипом, повертає скориговану адресу початку об'єкта. Якщо типи несумісні — повертає `nullptr`.

Ціна `dynamic_cast` набагато вища за `static_cast`: замість однієї інструкції додавання константи він виконує виклик функції, кілька непрямих звернень до пам'яті та лінійний пошук у графі спадкування RTTI.

## Експеримент 3: Пряме зчитування vtable у віртуальному спадкуванні

Дослідимо, як під капотом Itanium C++ ABI організовано пошук спільних віртуальних баз. Візьмемо клас із віртуальним спадкуванням `VirtualBase`:

:::tabs
```cpp
#include <iostream>
#include <cstdint>

class VirtualBase {
public:
    virtual void vfunc() { std::cout << "VirtualBase::vfunc\n"; }
    int v_data{777};
};

class DiamondDerived : virtual public VirtualBase {
public:
    void vfunc() override { std::cout << "DiamondDerived::vfunc\n"; }
    int d_data{888};
};

int main() {
    DiamondDerived obj;
    
    // Інтерпретуємо пам'ять об'єкта як масив слів
    uintptr_t* raw_obj = reinterpret_cast<uintptr_t*>(&obj);
    
    // Перше слово об'єкта — це vptr
    uintptr_t vptr = raw_obj[0];
    uintptr_t* vtable_entry = reinterpret_cast<uintptr_t*>(vptr);
    
    // В Itanium ABI метадані віртуальної бази лежать за від'ємними індексами
    ptrdiff_t offset_to_top = static_cast<ptrdiff_t>(vtable_entry[-2]);
    ptrdiff_t vbase_offset  = static_cast<ptrdiff_t>(vtable_entry[-3]);

    std::cout << "=== Дослідження метаданих vtable (Itanium ABI) ===\n";
    std::cout << "Адреса об'єкта DiamondDerived: " << &obj << "\n";
    std::cout << "Адреса vptr:                   0x" << std::hex << vptr << std::dec << "\n";
    std::cout << "Зсув offset-to-top (vtable[-2]): " << offset_to_top << " B\n";
    std::cout << "Зсув до VirtualBase (vtable[-3]): " << vbase_offset << " B\n";

    // Пряма перевірка адреси віртуальної бази через отриманий зсув
    char* obj_bytes = reinterpret_cast<char*>(&obj);
    VirtualBase* vbase_manual = reinterpret_cast<VirtualBase*>(obj_bytes + vbase_offset);
    
    std::cout << "Значення v_data через ручний зсув: " << vbase_manual->v_data << "\n";
    return 0;
}
```
```c
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

/* Моделювання структури повної таблиці Itanium ABI з метаданими */
typedef struct {
    ptrdiff_t vbase_offset;   /* Зсув до віртуальної бази: слот [-3] */
    ptrdiff_t offset_to_top;  /* Зсув до початку повного об'єкта: слот [-2] */
    void*     rtti_info;      /* Покажчик на RTTI: слот [-1] */
    void (*vfunc)(void*);     /* Точка входу: слот [0] */
} CompleteVTable;

typedef struct {
    int v_data;
} VirtualBaseData;

typedef struct {
    const void* vptr;         /* Вказує на поле vfunc у CompleteVTable */
    int d_data;
    VirtualBaseData vbase;    /* Спільна віртуальна база в кінці об'єкта */
} ManualDiamond;

static void manual_vfunc(void* self) {
    (void)self;
    printf("ManualDiamond::vfunc виконано\n");
}

static const CompleteVTable g_full_vtable = {
    .vbase_offset  = offsetof(ManualDiamond, vbase),
    .offset_to_top = 0,
    .rtti_info     = NULL,
    .vfunc         = manual_vfunc
};

int main(void) {
    ManualDiamond obj;
    obj.vptr = &g_full_vtable.vfunc; /* Точка входу vtable відповідає слоту [0] */
    obj.d_data = 888;
    obj.vbase.v_data = 777;

    /* Зчитування від'ємного зсуву з таблиці */
    const void** vtable_entry = (const void**)obj.vptr;
    ptrdiff_t vbase_offset = (ptrdiff_t)vtable_entry[-3];

    printf("=== Ручне читання зсувів віртуальної бази в C ===\n");
    printf("Зсув до віртуальної бази з vtable[-3]: %td байтів\n", vbase_offset);

    VirtualBaseData* vbase_ptr = (VirtualBaseData*)((char*)&obj + vbase_offset);
    printf("Значення vbase_ptr->v_data: %d\n", vbase_ptr->v_data);

    return 0;
}
```
:::

## Інженерні підсумки

1. **Множинне спадкування збільшує накладні витрати на пам'ять:** кожен додатковий базовий клас додає 8 байтів покажчика на віртуальну таблицю (`vptr`) та можливі байти набивки для вирівнювання полів.
2. **Низькорівневе приведення (`reinterpret_cast`) небезпечне для ієрархій:** воно не враховує внутрішнє розташування під-об'єктів і не виконує зміщення покажчика `this`, що спричиняє спотворення пам'яті та читання невідповідних полів.
3. **Віртуальні бази вимагають непрямої адресації:** доступ до даних віртуального предка не є константним зміщенням часу компіляції — він завжди вимагає попереднього зчитування зміщення з метаданих `vtable` (`vtable[-3]` або `vbtable`), що збільшує час виконання та навантаження на кеш процесора.
