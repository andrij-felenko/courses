# 📋 Довідник структур та інтерфейсів: GObject, kobject та COM

Цей довідник містить формалізований опис двійкових контрактів, розкладки структур у пам'яті, сигнатур функцій та інваріантів життєвого циклу для трьох провідних об'єктних моделей у мові C: GObject (простір користувача / GNOME), kobject (простір ядра Linux) та COM (двійковий стандарт компонентів Microsoft).

---

## 1. Підсистема GObject (GLib / GTK)

Об'єктна система GObject розмежовує метадані типу (структура класу `GTypeClass`, яка існує в пам'яті як єдиний синглтон на весь процес) та конкретний екземпляр з даними (`GTypeInstance`, який виділяється в купі на кожен створений об'єкт).

### Базові структури даних та їхній еквівалент у C++

:::tabs
```c
/* Числовий ідентифікатор типу в системі GType (зазвичай uintptr_t) */
typedef gsize GType;

/* Заголовок будь-якого екземпляра об'єкта */
struct _GTypeInstance {
    GTypeClass *g_class;           /* Вказівник на структуру класу (vtable) */
};

/* Заголовок будь-якої структури класу (синглтона) */
struct _GTypeClass {
    GType g_type;                  /* Зворотне посилання на зареєстрований GType */
};

/* Базовий об'єкт GObject */
struct _GObject {
    GTypeInstance  g_type_instance;/* Зсув 0: вказівник на клас */
    volatile guint ref_count;      /* Атомарний лічильник посилань */
    GData         *qdata;          /* Асоціативний список довільних атрибутів */
};

/* Базовий клас GObjectClass */
struct _GObjectClass {
    GTypeClass   g_type_class;     /* Зсув 0: GType */
    
    /* Таблиця конструкторів та деструкторів */
    GObject*   (*constructor)     (GType type, guint n_props, GObjectConstructParam *props);
    void       (*set_property)    (GObject *object, guint prop_id, const GValue *value, GParamSpec *pspec);
    void       (*get_property)    (GObject *object, guint prop_id, GValue *value, GParamSpec *pspec);
    void       (*dispose)         (GObject *object);   /* Розрив циклічних посилань */
    void       (*finalize)        (GObject *object);   /* Фінальне звільнення пам'яті */
    void       (*constructed)     (GObject *object);
};
```
```cpp
// Концептуальне відображення об'єктної моделі GObject на класи C++20
#pragma once
#include <cstdint>
#include <memory>
#include <string_view>
#include <unordered_map>
#include <any>

using GType = std::uintptr_t;

// Еквівалент метакласу GTypeClass (визначає метадані та поведінку типу)
class ObjectClass {
public:
    virtual ~ObjectClass() = default;
    [[nodiscard]] virtual GType type_id() const noexcept = 0;
    [[nodiscard]] virtual std::string_view type_name() const noexcept = 0;
};

// Еквівалент екземпляра GObject з інкапсульованим керуванням життям
class Object : public std::enable_shared_from_this<Object> {
public:
    virtual ~Object() = default;

    virtual void dispose() noexcept {
        // Розрив можливих циклічних зв'язків
        m_qdata.clear();
    }

    void set_qdata(std::string_view key, std::any value) {
        m_qdata.insert_or_assign(std::string(key), std::move(value));
    }

    [[nodiscard]] std::any get_qdata(std::string_view key) const {
        if (auto it = m_qdata.find(std::string(key)); it != m_qdata.end()) {
            return it->second;
        }
        return {};
    }

private:
    std::unordered_map<std::string, std::any> m_qdata;
};
```
:::

### Детальний опис полів та інваріантів розкладки

1. **Поле `g_class` (зсув 0 байтів у `GTypeInstance`):**
   Будь-яка функція рантайму GObject може безпечно отримати покажчик на vtable об'єкта через розіменування `*(GTypeClass**)instance`. Це забезпечує поліморфну диспетчеризацію з фіксованим зсувом `0` для всієї ієрархії нащадків.

2. **Поле `ref_count` (зсув 8 байтів у `GObject` на 64-бітній платформі):**
   Цілочисельний лічильник сильних посилань. Збільшується через `g_object_ref()` та зменшується через `g_object_unref()`. Модифікація виконується атомарними процесорними інструкціями (наприклад, `LOCK XADD` на архітектурі x86_64), що гарантує потокобезпечність операцій володіння.

3. **Поле `qdata` (зсув 16 байтів у `GObject`):**
   Покажчик на динамічний масив пар «ключ-значення» (`GQuark` -> `gpointer`). Використовується для асоціювання довільних даних з об'єктом без розширення самої C-структури, а також для збереження слабких посилань (weak references) та прив'язок до мовних обгорток (Python/JS).

4. **Система властивостей та універсальних контейнерів `GValue`:**
   Властивості GObject описуються специфікаціями `GParamSpec`. Встановлення значення через `g_object_set_property()` використовує типізований контейнер `GValue`. Якщо переданий тип несумісний зі специфікацією, рантайм фіксує помилку у журналі без ризику пошкодження пам'яті.

### Основні функції API GObject

| Функція | Сигнатура | Призначення, контракти та обробка помилок |
| :--- | :--- | :--- |
| `g_type_register_static` | `GType g_type_register_static(GType parent_type, const gchar *type_name, const GTypeInfo *info, GTypeFlags flags)` | Реєструє новий незмінний тип у глобальному дереві типів. Приймає розміри структури екземпляра та структури класу, а також покажчики на `class_init` та `instance_init`. Повертає унікальний `GType`. Якщо ім'я вже зайняте, генерує критичну помилку `g_critical()`. |
| `g_object_new` | `gpointer g_object_new(GType object_type, const gchar *first_prop_name, ...)` | Виділяє пам'ять екземпляра в купі через `g_slice_alloc0()` або `g_malloc0()`, ініціалізує лічильник `ref_count = 1`, викликає ланцюжок ініціалізаторів екземплярів `instance_init` від базового до похідного, і встановлює передані властивості. |
| `g_object_ref` | `gpointer g_object_ref(gpointer object)` | Атомарно інкрементує лічильник `ref_count`. Перевіряє вказівник на `NULL` та коректність типу за допомогою макросів перевірки. Повертає переданий покажчик `object`, що дозволяє запис у стилі `self->target = g_object_ref(target)`. |
| `g_object_unref` | `void g_object_unref(gpointer object)` | Атомарно декрементує `ref_count`. Якщо значення досягає нуля, запускає двоетапний процес знищення: спершу фазу `dispose`, а після повторної перевірки лічильника — фазу `finalize` зі звільненням пам'яті. |
| `g_signal_connect` | `gulong g_signal_connect(gpointer instance, const gchar *detailed_signal, GCallback c_handler, gpointer data)` | Реєструє функцію зворотного виклику `c_handler` у таблиці обробників сигналу. Повертає унікальний числовий ідентифікатор `handler_id` для подальшого від'єднання через `g_signal_handler_disconnect()`. |

### Двоетапне знищення: протокол розриву циклів (dispose vs finalize)

У граф-орієнтованих архітектурах інтерфейсу користувача (наприклад, вікно утримує кнопку, а кнопка утримує зворотне посилання на вікно) звичайний деструктор спричиняє витік пам'яті через взаємне блокування лічильників посилань. GObject розв'язує цю проблему через поділ життєвого циклу знищення на два кроки:

1. **Фаза `dispose` (розрив зв'язків):**
   - Викликається під час падіння лічильника посилань до нуля, а також може викликатися явно клієнтським кодом (наприклад, при закритті вікна `gtk_window_destroy()`).
   - Об'єкт зобов'язаний скинути (обнулити) всі посилання на інші екземпляри `GObject` за допомогою макроса `g_clear_object(&self->priv->child)`.
   - Об'єкт залишається цілісною сутністю в пам'яті: його `GTypeInstance` і `g_class` все ще валідні, і будь-який вхідний виклик методу повинен коректно повертати значення за замовчуванням без розіменування вивільнених полів.
   - Метод `dispose` може викликатися багаторазово, тому кожна операція очищення мусить бути ідемпотентною.

2. **Фаза `finalize` (фізичне звільнення пам'яті):**
   - Викликається строго один раз безпосередньо перед передачею блока пам'яті алокатору.
   - Звільняє системні дескриптори (сокети, файли, семафори POSIX) та сирі динамічні буфери (`g_free()`), які не є об'єктами `GObject`.
   - Після завершення `finalize` пам'ять екземпляра повертається в операційну систему.

---

## 2. Модель об'єктів ядра Linux (kobject та driver model)

Модель ядра спирається на інтрузивне вбудовування структури `struct kobject` безпосередньо у внутрішні структури пристроїв, шин та драйверів.

### Базові структури ядра та концептуальна модель C++

:::tabs
```c
/* Структури простору ядра Linux */
struct kobject {
    const char          *name;     /* Ім'я об'єкта (каталог у sysfs) */
    struct list_head     entry;    /* Входження до списку kset */
    struct kobject      *parent;   /* Батьківський kobject (ієрархія) */
    struct kset         *kset;     /* Група/підсистема */
    const struct kobj_type *ktype; /* Таблиця операцій та деструктор */
    struct kernfs_node  *sd;       /* Вузол віртуальної ФС sysfs */
    struct kref          kref;     /* Атомарний лічильник посилань */
    unsigned int state_initialized:1;
    unsigned int state_in_sysfs:1;
    unsigned int state_add_uevent_sent:1;
    unsigned int state_remove_uevent_sent:1;
    unsigned int uevent_suppress:1;
};

struct kobj_type {
    void (*release)(struct kobject *kobj);        /* Обов'язковий деструктор */
    const struct sysfs_ops *sysfs_ops;            /* Обробники читання/запису */
    const struct attribute_group **default_groups;/* Файли атрибутів у /sys */
};

struct sysfs_ops {
    ssize_t (*show)(struct kobject *kobj, struct attribute *attr, char *buf);
    ssize_t (*store)(struct kobject *kobj, struct attribute *attr, const char *buf, size_t count);
};
```
```cpp
// Концептуальне відображення інтрузивного вузла ядра в C++
#pragma once
#include <atomic>
#include <string>
#include <functional>
#include <string_view>

struct KObjectType;

// Інтрузивний блок ядра, що вбудовується всередину об'єкта
class KObject {
public:
    KObject(std::string name, const KObjectType* type)
        : m_name(std::move(name)), m_ktype(type), m_refcount(1) {}

    void get() noexcept {
        m_refcount.fetch_add(1, std::memory_order_relaxed);
    }

    void put() noexcept;

    [[nodiscard]] const std::string& name() const noexcept { return m_name; }

private:
    std::string m_name;
    const KObjectType* m_ktype;
    std::atomic<int> m_refcount;
};

struct KObjectType {
    std::function<void(KObject*)> release;
};

inline void KObject::put() noexcept {
    if (m_refcount.fetch_sub(1, std::memory_order_acq_rel) == 1) {
        if (m_ktype && m_ktype->release) {
            m_ktype->release(this);
        }
    }
}
```
:::

### Основні функції ядра Linux

| Функція / Макрос | Сигнатура | Поведінка, контракти та обмеження |
| :--- | :--- | :--- |
| `container_of` | `container_of(ptr, type, member)` | Макрос компілятора: обчислює адресу структури-господаря за формулою `(type*)((char*)ptr - offsetof(type, member))`. Виконує перевірку типу покажчика під час компіляції за допомогою оператора `typeof()`. |
| `kobject_init` | `void kobject_init(struct kobject *kobj, const struct kobj_type *ktype)` | Обнуляє структуру `kobject`, виставляє початкове значення лічильника `kref = 1` та прив'язує покажчик `ktype`. Об'єкт переходить у стан `state_initialized = 1`. |
| `kobject_add` | `int kobject_add(struct kobject *kobj, struct kobject *parent, const char *fmt, ...)` | Додає об'єкт до ієрархії ядра, встановлює батьківський вузол `parent` та створює відповідну директорію у файловій системі `sysfs`. При успіху повертає `0`, при помилці виділення пам'яті — від'ємний код (`-ENOMEM`). |
| `kobject_init_and_add` | `int kobject_init_and_add(struct kobject *kobj, const struct kobj_type *ktype, struct kobject *parent, const char *fmt, ...)` | Об'єднує виклики `kobject_init` та `kobject_add` в одну атомарну операцію. Якщо створення в sysfs завершилося помилкою, функція автоматично зменшує лічильник через `kobject_put()`. |
| `kobject_get` | `struct kobject *kobject_get(struct kobject *kobj)` | Атомарно збільшує `kref`. Якщо покажчик `kobj == NULL` або об'єкт перебуває в процесі видалення, функція повертає `NULL`. |
| `kobject_put` | `void kobject_put(struct kobject *kobj)` | Атомарно зменшує лічильник `kref`. Коли лічильник стає рівним нулю, ядро асинхронно викликає метод `kobj->ktype->release(kobj)`. |

### Головне правило безпеки kobject
Жодна структура ядра, що містить всередині `struct kobject`, не має права викликати функцію `kfree()` для власного блоку пам'яті напряму з робочого коду чи функції вивантаження драйвера `driver_unregister()`. Поки на пристрій відкрито хоча б один файловий дескриптор у `/sys` або існує посилання у підсистемі, пам'ять зобов'язана жити. Фізичне звільнення зовнішньої структури через `kfree(container_of(kobj, struct my_device, kobj))` має відбуватися **виключно** всередині колбека `release()`.

---

## 3. Microsoft Component Object Model (COM)

COM визначає двійковий стандарт віртуальної таблиці (vtable), який робить об'єкти в пам'яті сумісними між C, C++, Rust та асемблером без потреби перекомпіляції.

### Базовий інтерфейс IUnknown у C та C++

:::tabs
```c
/* Оголошення IUnknown мовою C */
#include <windows.h>

typedef struct IUnknownVtbl {
    /* [0] Запит інтерфейсу за GUID */
    HRESULT (*QueryInterface)(void *This, REFIID riid, void **ppvObject);
    
    /* [1] Атомарне додавання посилання */
    ULONG (*AddRef)(void *This);
    
    /* [2] Атомарне зменшення посилання та деструкція */
    ULONG (*Release)(void *This);
} IUnknownVtbl;

typedef struct IUnknown {
    const IUnknownVtbl *lpVtbl;    /* Зсув 0: покажчик на vtable */
} IUnknown;
```
```cpp
// Оголошення IUnknown мовою C++ (чистий абстрактний клас з віртуальними методами)
#pragma once
#include <unknwn.h>

// Компілятор C++ генерує ідентичну двійкову vtable з трьома покажчиками
struct ICustomUnknown {
    virtual HRESULT STDMETHODCALLTYPE QueryInterface(
        REFIID riid, 
        void **ppvObject) = 0;

    virtual ULONG STDMETHODCALLTYPE AddRef() = 0;

    virtual ULONG STDMETHODCALLTYPE Release() = 0;

    virtual ~ICustomUnknown() = default;
};
```
:::

### Стандартні коди помилок HRESULT

| Код HRESULT | Числове значення | Семантичний опис |
| :--- | :--- | :--- |
| `S_OK` | `0x00000000` | Успішне завершення виклику методу. |
| `S_FALSE` | `0x00000001` | Виклик завершився успішно, але повернув логічний негативний результат (наприклад, досягнуто кінця потоку або елемент не знайдено). |
| `E_NOINTERFACE` | `0x80004002` | Запитаний ідентифікатор інтерфейсу `riid` не підтримується цим об'єктом. |
| `E_POINTER` | `0x80004003` | Вихідний параметр для покажчика на інтерфейс `ppvObject` дорівнює `NULL`. |
| `E_UNEXPECTED` | `0x8000FFFF` | Внутрішня невідновна помилка компонента під час виконання операції. |
| `E_OUTOFMEMORY` | `0x8007000E` | Не вдалося виділити необхідний блок пам'яті для створення об'єкта або буфера. |

### Математичні аксіоми контракту QueryInterface
1. **Ідентичність об'єкта (Object Identity):**
   Запит інтерфейсу `IID_IUnknown` через будь-який інтерфейс, реалізований об'єктом, зобов'язаний завжди повертати точне однакове числове значення вказівника. Порівняння покажчиків `pUnk1 == pUnk2` є єдиним стандартизованим способом перевірити, чи належать два різні інтерфейси одному фізичному екземпляру компонента.
2. **Симетричність (Symmetry):**
   Якщо виклик `pA->QueryInterface(IID_B, &pB)` завершився з `S_OK`, то наступний виклик `pB->QueryInterface(IID_A, &pA2)` над отриманим покажчиком також обов'язково повертає `S_OK`.
3. **Транзитивність (Transitivity):**
   Якщо через інтерфейс `A` можна отримати інтерфейс `B`, а через `B` можна отримати інтерфейс `C`, то запит інтерфейсу `C` безпосередньо через покажчик `A` гарантовано повертає успіх.
4. **Стабільність у часі (Time Invariance):**
   Множина інтерфейсів, які підтримує об'єкт, є фіксованою протягом усього його життя. Якщо перший запит `QueryInterface(IID_X)` повернув `E_NOINTERFACE`, усі наступні виклики з тим самим `IID_X` для цього екземпляра повинні повертати `E_NOINTERFACE`. Динамічне додавання або видалення інтерфейсів заборонено специфікацією COM.

### Потокові моделі COM та маршалінг інтерфейсів

У системі COM взаємодія між потоками суворо регламентується моделлю апартаментів (англ. *Apartments*):
- **Single-Threaded Apartment (STA):** Усі виклики методів об'єкта виконуються виключно в тому потоці, який його створив. Якщо інший потік викликає метод COM-об'єкта з STA, система автоматично виконує синхронізацію через чергу повідомлень Windows (`GetMessage`/`DispatchMessage`). Це усуває стан гонитви (race condition), але вимагає регулярного прокручування циклу подій.
- **Multi-Threaded Apartment (MTA):** Об'єкт може одночасно викликатися з довільної кількості потоків. Усі методи зобов'язані бути повністю потокобезпечними (інкапсулювати критичні секції або м'ютекси), а лічильники посилань `AddRef()`/`Release()` мають використовувати виключно інтерлоковані інструкції `InterlockedIncrement()` та `InterlockedDecrement()`.
- **Передача покажчиків між апартаментами (Marshalling):** Пряма передача сирого вказівника на інтерфейс між різними апартаментами без маршалінгу (`CoMarshalInterThreadInterfaceInStream`) призводить до пошкодження стека або взаємного блокування потоків. Рантайм COM створює спеціальний проксі-об'єкт (англ. *proxy/stub*), який упаковує параметри виклику в пакет і передає його цільовому потоку.
