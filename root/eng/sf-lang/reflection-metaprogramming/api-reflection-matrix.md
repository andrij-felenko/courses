# 📋 Довідник рефлексивних інтерфейсів і моделей метапрограмування

Цей довідник містить систематизований опис сигнатур, структур даних, таблиць контрактів, винятків та характеристик продуктивності для провідних систем рефлексії та метапрограмування. Він слугує практичним орієнтиром для вибору архітектурного підходу: від низькорівневих інтерфейсів C++ (RTTI та стандарту C++26 P2996) до віртуальних машин JVM, платформи .NET CLR, прекомпіляторів Qt та макросистем Rust і Lisp.

---

### Матриця можливостей за мовами та середовищами

| Мова / Технологія | Механізм метаданих | Час роботи | Інтроспекція (читання) | Інтероспекція (зміна) | Генерація коду | Накладні витрати пам'яті | Втрата швидкодії виклику |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **C++ (RTTI)** | `std::type_info` у `vtable` | Runtime | Лише ім'я та спадкування | Ні | Ні | +8 байт на vptr + таблиці типів | ~1–3 нс (vtable lookup) |
| **C++26 (P2996)** | `std::meta::info` у AST | Compile-time | Повна (поля, типи, атрибути) | Ні (стан незмінний) | Так (сплайсинг `[:...:]`) | 0 байт у двійковому образі | 0 нс (повний інлайнінг) |
| **Java Reflection** | `Class<T>`, `Method`, `Field` | Runtime | Повна (включно з приватними) | Так (через `setAccessible`) | Через генерацію байткоду | Метадані всіх завантажених класів | 15–50 нс (boxing, security) |
| **C# .NET Reflection** | Таблиці метаданих CLI | Runtime | Повна (атрибути, властивості) | Так (DynamicMethod, Emit) | Так (`Reflection.Emit`) | Таблиці типів у кожній збірці | 10–40 нс (можливий JIT-інлайн) |
| **Qt (MOC)** | Таблиці `QMetaObject` | Runtime | Методи, сигнали, слоти, Q_PROPERTY | Так (виклик за числовим ID) | На етапі прекомпіляції | Статичні масиви в `.rodata` | 5–15 нс (пошук за індексом) |
| **Rust Macros** | Токени `TokenStream` (AST) | Compile-time | В межах макроса | Ні | Так (`proc_macro`) | 0 байт у двійковому образі | 0 нс (мономорфізація) |
| **Common Lisp** | S-вирази (Homoiconicity) | Обидва | Повна через CLOS MOP | Так (перевизначення класів) | Так (`defmacro`) | Динамічне середовище | Залежить від компілятора |

---

### 1. C++: Статична рефлексія P2996 (C++26)

Статична рефлексія C++26 стандартизує модель інтроспекції та генерації коду безпосередньо всередині компілятора. Вся робота відбувається в константному контексті `constexpr` або `consteval`, оперуючи непрозорим скалярним значенням дескриптора `std::meta::info`.

#### Контракт базових операторів

Оператор підйому `^^` (англ. *reflection operator*) приймає назву типу, вираз, шаблон, функцію, простір імен або змінну і повертає дескриптор `std::meta::info`. Значення цього дескриптора є константним літералом часу компіляції і може передаватися в будь-які `constexpr`-функції як звичайне число чи покажчик.

Оператор зрощення `[: r :]` (англ. *splice operator*) виконує зворотну операцію: він бере дескриптор `r` і вставляє відповідну сутність назад у синтаксичне дерево абстрактної машини компілятора. Залежно від граматичного контексту, результат сплайсингу може інтерпретуватися як вираз, назва типу або шаблонний аргумент.

```cpp
namespace std::meta {
    // Перевірка категорій сутностей
    consteval bool is_type(info r);
    consteval bool is_variable(info r);
    consteval bool is_function(info r);
    consteval bool is_nonstatic_data_member(info r);

    // Отримання властивостей та метрик
    consteval string_view name_of(info r);
    consteval string_view display_name_of(info r);
    consteval info        type_of(info r);
    consteval size_t      offset_of(info r);
    consteval size_t      size_of(info r);
    consteval size_t      alignment_of(info r);

    // Дослідження структури та ієрархій
    consteval vector<info> members_of(info r);
    consteval vector<info> nonstatic_data_members_of(info r);
    consteval vector<info> bases_of(info r);
    consteval vector<info> enumerators_of(info r);

    // Генерація нових сутностей
    consteval info identifier(string_view name);
    consteval info substitute(info template_entity, span<const info> args);
}
```

Усі функції простору імен `std::meta` гарантовано детерміновані. Будь-яка спроба передати недійсний дескриптор або викликати функцію з порушенням семантики (наприклад, викликати `offset_of` для типу або функції) призводить до негайної помилки збірки (`compile-time error`).

---

### 2. Java Reflection API (`java.lang.reflect`)

У середовищі JVM рефлексія надає повний доступ до структури завантажених класів під час виконання програми через об'єкт-дескриптор `java.lang.Class<T>`.

#### Життєвий цикл та робота з безпекою

Отримання дескриптора класу можливе трьома шляхами: через статичний літерал типу `TargetClass.class`, через метод примірника `object.getClass()`, або динамічно через завантажувач класів за текстовою назвою `Class.forName("com.example.TargetClass")`.

При роботі з полями та методами віртуальна машина розрізняє методи публічного інтерфейсу та внутрішні члени:
- Методи `getFields()` та `getMethods()` повертають лише публічні члени класу, включно з успадкованими від суперкласів та інтерфейсів.
- Методи `getDeclaredFields()` та `getDeclaredMethods()` повертають усі члени, оголошені безпосередньо в цьому класі (включно з `private`, `protected` та `package-private`), але ігнорують успадковані сутності.

```java
// Отримання та маніпуляція полями
Class<?> clazz = UserProfile.class;
Field field = clazz.getDeclaredField("secretToken");

// Примусове вимкнення перевірок контролю доступу JVM
field.setAccessible(true);

// Читання та модифікація стану об'єкта
Object value = field.get(userInstance);
field.set(userInstance, "new_secret_value");

// Динамічний пошук та виклик методу
Method method = clazz.getDeclaredMethod("updateBalance", double.class, boolean.class);
method.setAccessible(true);
Object result = method.invoke(userInstance, 100.50, true);
```

#### Механізм динамічних проксі (Dynamic Proxies)

Клас `java.lang.reflect.Proxy` дозволяє створювати примірники інтерфейсів у реальному часі без генерації вихідного коду. Віртуальна машина створює синтетичний клас у пам'яті, який реалізує зазначені інтерфейси та перенаправляє всі виклики методів у єдиний обробник `InvocationHandler`:

```java
UserProfileService proxy = (UserProfileService) Proxy.newProxyInstance(
    UserProfileService.class.getClassLoader(),
    new Class<?>[] { UserProfileService.class },
    new InvocationHandler() {
        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            System.out.println("Логування перед викликом: " + method.getName());
            Object result = method.invoke(targetInstance, args);
            System.out.println("Логування після виклику");
            return result;
        }
    }
);
```

#### Винятки та обробка помилок у рантаймі
- `ClassNotFoundException` — виникає при виклику `Class.forName()`, якщо завантажувач не знайшов відповідний `.class` файл у classpath.
- `NoSuchFieldException` / `NoSuchMethodException` — запитаного члена з такою назвою або сигнатурою параметрів не існує.
- `IllegalAccessException` — порушення інкапсуляції (спроба читання приватного поля без виклику `setAccessible(true)` або в умовах жорсткого модулятора Java 9+ JPMS).
- `InvocationTargetException` — метод, викликаний через `Method.invoke()`, викинув виняток під час свого виконання (оригінальний виняток доступний через метод `getCause()`).

---

### 3. C# .NET (`System.Reflection`)

Платформа .NET зберігає повні реляційні таблиці метаданих у заголовках двійкових файлів формату Portable Executable (PE) за стандартом ECMA-335. Це дозволяє здійснювати високошвидкісну інтроспекцію типів, роботу з декларативними атрибутами та генерацію проміжного байткоду CIL у реальному часі.

#### Дослідження структури та прапорці зв'язування (BindingFlags)

Пошук членів у .NET вимагає явної вказівки бітових прапорців `BindingFlags`, що контролюють область пошуку:

```csharp
using System;
using System.Reflection;

Type type = typeof(UserProfile);

// Пошук з фільтрацією за областю видимості та статичністю
BindingFlags flags = BindingFlags.Public | 
                     BindingFlags.NonPublic | 
                     BindingFlags.Instance | 
                     BindingFlags.Static;

PropertyInfo[] properties = type.GetProperties(flags);
foreach (PropertyInfo prop in properties) {
    Console.WriteLine($"Властивість: {prop.Name}, Тип: {prop.PropertyType.Name}");
    if (prop.CanRead) {
        object val = prop.GetValue(instance);
    }
}

// Пошук декларативних атрибутів
MyCustomAttribute attr = type.GetCustomAttribute<MyCustomAttribute>();
if (attr != null) {
    Console.WriteLine($"Конфігурація атрибута: {attr.ConfigurationName}");
}
```

#### Генерація байткоду на льоту (`System.Reflection.Emit`)

Для усунення оверхеду від рефлексивних викликів .NET дозволяє створювати методи на рівні машинних команд CIL безпосередньо під час роботи програми за допомогою класу `DynamicMethod`:

```csharp
using System.Reflection.Emit;

// Створення динамічного методу складання двох цілих чисел
DynamicMethod dynamicAdd = new DynamicMethod(
    "FastAdd", 
    typeof(int), 
    new Type[] { typeof(int), typeof(int) }
);

ILGenerator il = dynamicAdd.GetILGenerator();
il.Emit(OpCodes.Ldarg_0); // Завантаження першого аргументу
il.Emit(OpCodes.Ldarg_1); // Завантаження другого аргументу
il.Emit(OpCodes.Add);     // Виконання складання
il.Emit(OpCodes.Ret);     // Повернення результату

// Компіляція у нативний делегат
Func<int, int, int> fastAddDelegate = 
    (Func<int, int, int>)dynamicAdd.CreateDelegate(typeof(Func<int, int, int>));

int result = fastAddDelegate(40, 2); // Швидкість виконання дорівнює нативному коду
```

---

### 4. Qt Meta-Object System (`QMetaObject`)

Метаоб'єктна модель Qt створена для надання нативному коду C++ можливостей динамічного зв'язування компонентів, передачі повідомлень (сигнали та слоти) та динамічного читання властивостей графічного інтерфейсу (QML).

#### Внутрішня будова таблиці `qt_meta_data`

Препроцесор MOC генерує статичні константні масиви цілих чисел, які лінкуються в секцію `.rodata` бінарного файлу:

```cpp
// Структура заголовка метаданих Qt MOC
static const uint qt_meta_data_DeviceController[] = {
    // Зміст заголовка (Header):
    // 0: Ревізія формату метаданих MOC (наприклад, 8)
    // 1: Зміщення назви класу в таблиці рядків
    // 2, 3: Кількість методів класу та індекс початку їхнього опису
    // 4, 5: Кількість властивостей Q_PROPERTY та їхній індекс
    // 6, 7: Кількість перелічувачів Q_ENUM та їхній індекс
    // 8, 9: Кількість конструкторів та їхній індекс
    // 10: Прапорці метаоб'єкта
    // 11: Кількість зареєстрованих сигналів
    8,       // Revision
    0,       // Classname offset
    3, 14,   // 3 методи, зміщення опису = 14
    1, 26,   // 1 властивість, зміщення = 26
    0, 0,    // 0 перелічувачів
    0, 0,    // 0 конструкторів
    0,       // Flags
    1,       // 1 сигнал (завжди передує слотам)
};
```

#### Публічний інтерфейс інтроспекції та диспетчеризації

Клас `QMetaObject` надає повний набір функцій для дослідження та виклику методів за числовими індексами:
- `const char* className() const` — повертає рядкове ім'я класу.
- `int methodCount() const` та `QMetaMethod method(int index) const` — перебір методів, сигналів та слотів.
- `int propertyCount() const` та `QMetaProperty property(int index) const` — перебір зареєстрованих властивостей `Q_PROPERTY`.
- `int indexOfSignal(const char* signal) const` та `int indexOfSlot(const char* slot) const` — швидкий числовий пошук за сигнатурою.
- `static bool invokeMethod(QObject* obj, const char* member, Qt::ConnectionType type, QGenericReturnArgument ret, ...)` — універсальний асинхронний або синхронний виклик методу через чергу подій потоку.

---

### 5. Rust: Процедурні макроси (`proc_macro`) та AST-інтроспекція

У мові Rust статичне метапрограмування виконується шляхом прямої трансформації абстрактного синтаксичного дерева під час компіляції. Процедурні макроси є окремими динамічними бібліотеками, що виконуються компілятором `rustc`.

#### Публічний контракт `proc_macro_derive`
```rust
use proc_macro::TokenStream;
use syn::{parse_macro_input, DeriveInput, Data, Fields};
use quote::quote;

#[proc_macro_derive(MySerializer)]
pub fn derive_serializer(input: TokenStream) -> TokenStream {
    // 1. Парсинг вхідного потоку токенів у типізоване AST дерево
    let ast = parse_macro_input!(input as DeriveInput);
    let name = &ast.ident;

    // 2. Інтроспекція полів структури
    let field_names = match &ast.data {
        Data::Struct(data_struct) => match &data_struct.fields {
            Fields::Named(fields_named) => {
                fields_named.named.iter().map(|f| &f.ident).collect::<Vec<_>>()
            }
            _ => panic!("Підтримуються лише іменовані структури!"),
        },
        _ => panic!("Підтримуються лише структури, а не enum чи union!"),
    };

    // 3. Генерація коду за допомогою квазіцитування quote!
    let expanded = quote! {
        impl #name {
            pub fn print_fields(&self) {
                #(
                    println!("{}: {:?}", stringify!(#field_names), self.#field_names);
                )*
            }
        }
    };

    // 4. Повернення згенерованого AST назад у компілятор
    TokenStream::from(expanded)
}
```

Модель процедурних макросів гарантує нульові витрати у фінальному бінарнику: якщо в процесі розгортання макроса виявлено помилку, макрос викидає діагностичне повідомлення `syn::Error`, яке компілятор підсвічує безпосередньо у вихідному коді користувача з точним номером рядка та стовпця.

---

### 6. Common Lisp: Протокол метаоб'єктів (CLOS MOP)

У системі Common Lisp об'єктна модель повністю відкрита для програміста через набір стандартизованих функцій інтроспекції та інтероспекції бібліотеки `closer-mop`.

#### Інтроспекція класів та слотів (полів)
```lisp
;; Отримання списку всіх зареєстрованих полів (слотів) класу
(defun list-class-slots (class-name)
  (let ((class-meta (find-class class-name)))
    ;; Ініціалізація та фіналізація метакласу при потребі
    (unless (c2mop:class-finalized-p class-meta)
      (c2mop:finalize-inheritance class-meta))
    ;; Читання метаоб'єктів прямих та успадкованих слотів
    (mapcar #'c2mop:slot-definition-name
            (c2mop:class-slots class-meta))))

;; Динамічне читання значення поля за назвою символу
(defun get-slot-dynamic (instance slot-symbol)
  (slot-value instance slot-symbol))
```

#### Інтероспекція та зміна поведінки
CLOS MOP дозволяє змінювати порядок лінеаризації множинного спадкування через метод `compute-class-precedence-list`, фільтрувати методи перед диспетчеризацією через `compute-applicable-methods-using-classes` та перехоплювати читання і запис будь-якого поля через `slot-value-using-class`. Це робить Lisp найпотужнішим динамічним середовищем обчислювальної рефлексії, де мова здатна повністю трансформувати власні правила роботи під час виконання програми.
