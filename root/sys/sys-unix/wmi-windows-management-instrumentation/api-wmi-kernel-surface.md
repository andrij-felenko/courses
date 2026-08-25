# 📋 Довідник API ядра Linux для ACPI-WMI

Цей довідник надає вичерпний опис публічних структур даних, системних макросів, функцій ядра Linux для роботи з підсистемою ACPI-WMI (`<linux/wmi.h>`), а також детальний аналіз будови віртуальної файлової системи sysfs (`/sys/bus/wmi/devices/`).

Взаємодія ядра з пристроями WMI базується на фундаментальних принципах Linux Device Model: кожен виявлений у таблицях DSDT або SSDT GUID реєструється як окремий екземпляр пристрою на віртуальній шині `wmi_bus_type`. Це дозволяє розробникам писати декларативні драйвери ядра, які автоматично зв'язуються з апаратурою на основі таблиць відповідності GUID та модаліасів.

---

## 1. Основні структури даних ядра та їхній інваріант

### `struct wmi_device`
Представляє окремий пристрій WMI на шині `wmi_bus_type`. Драйвери отримують вказівник на цю структуру під час виклику методу `.probe()` та під час отримання асинхронних сповіщень.

```c
struct wmi_device {
    struct device dev;
    /* Внутрішні поля ядра: GUID, object_id, прапорці _WDG */
};
```

Структура вбудовує базовий об'єкт `struct device dev`, що дозволяє розробнику використовувати стандартні системні функції ядра на кшталт `dev_info()`, `dev_err()`, `dev_set_drvdata()`, `dev_get_drvdata()`, а також створювати індивідуальні атрибути та групи файлів у sysfs для управління пристроєм.

Внутрішньо ядро пов'язує `struct wmi_device` з відповідним маппінгом із таблиці `_WDG`. Об'єкт зберігає інформацію про 36-символьний рядок GUID, двосимвольний ACPI Object ID, прапорці доступу та кількість екземплярів пристрою (`instance_count`).

### `struct wmi_driver`
Описує драйвер пристрою WMI, який реєструється у підсистемі за допомогою спеціалізованого макросу `module_wmi_driver()`.

| Поле | Тип | Опис та призначення |
| :--- | :--- | :--- |
| `driver` | `struct device_driver` | Базова структура драйвера моделі пристроїв Linux (ім'я драйвера, модуль `owner`). |
| `id_table` | `const struct wmi_device_id *` | Таблиця сумісних GUID, яка обов'язково завершується порожнім елементом `{}`. |
| `probe` | `int (*)(struct wmi_device *, const void *)` | Функція ініціалізації пристрою при прив'язці сумісного GUID на шині WMI. |
| `remove` | `void (*)(struct wmi_device *)` | Функція вивантаження та деініціалізації ресурсів при вивантаженні модуля. |
| `notify` | `void (*)(struct wmi_device *, union acpi_object *)` | Зворотно-викликова функція (callback) для обробки асинхронних подій WMI. |
| `no_notify_data` | `bool` | Прапорець, що вказує ядру не викликати AML-метод `_WED` при отриманні сповіщення. |

### `struct wmi_device_id`
Елемент таблиці маппінгу ідентифікаторів, який визначає, які саме GUID спроможний обслуговувати даний модуль ядра.

```c
struct wmi_device_id {
    const char guid_string[37]; // Рядок GUID у форматі "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    const void *context;        // Довільний вказівник на приватний контекст розробника
};
```

Поле `guid_string` містить канонічний текстовий рядок GUID. Поле `context` є довільним вказівником, який передається другим аргументом у функцію `.probe()`. Це дозволяє використовувати один і той самий обробник `.probe()` для різних GUID, розрізняючи їх за переданою в контексті структурою конфігурації.

### `struct wmi_block`
Внутрішня структура ядра Linux (`drivers/platform/x86/wmi.c`), яка обгортає екземпляр пристрою WMI та зберігає метадані ACPI-вузла:

```c
struct wmi_block {
    struct wmi_device wdev;
    struct list_head list;
    struct guid_block gblock;
    acpi_handle handle;
    struct mutex char_mutex;
};
```

Структура `wmi_block` об'єднує екземпляр `wmi_device` з низькорівневим ACPI-хендлом (`acpi_handle`), що вказує на батьківський ACPI-пристрій `PNP0C14` у просторі імен DSDT. М'ютекс `char_mutex` використовується для впорядкування послідовних викликів методів та запобігання стану гонитви при одночасному зверненні кількох процесів простору користувача.

---

## 2. Механізм реєстрації, прив'язки та життєвого циклу `wmi_driver`

Підсистема WMI використовує загальні принципи Linux Device Model для автоматичного зв'язування драйверів із виявленими пристроями.

### Макрос `module_wmi_driver` та реєстрація в ядрі

Для усунення стандартного шаблонного коду (boilerplate) ядро надає макрос `module_wmi_driver()`. Він автоматично генерує функції ініціалізації (`init`) та завершення (`exit`) модуля ядра:

```c
#define module_wmi_driver(__wmi_driver) \
    module_driver(__wmi_driver, wmi_driver_register, wmi_driver_unregister)
```

При завантаженні модуля виконується функція `wmi_driver_register(struct wmi_driver *driver)`. Вона виконує такі підготовчі кроки:

1. Встановлює поле `driver.bus = &wmi_bus_type`, реєструючи драйвер на віртуальній шині WMI.
2. Призначає системні обробники шини для викликів `probe`, `remove` та `shutdown`.
3. Викликає підсистему ядра `driver_register(&driver->driver)`, що ініціює обхід списку зареєстрованих пристроїв WMI та запускає процедуру зіставлення (matching).

При вивантаженні модуля викликається `wmi_driver_unregister(struct wmi_driver *driver)`, яка відв'язує драйвер від усіх пристроїв, викликає їхні процедури `.remove()` та видаляє реєстраційний запис із шини `wmi_bus_type`.

### Алгоритм зіставлення на шині `wmi_bus_match`

Коли на шині WMI з'являється новий пристрій або реєструється новий драйвер, підсистема ядра викликає функцію зіставлення `wmi_bus_match(struct device *dev, struct device_driver *drv)`:

```c
static int wmi_bus_match(struct device *dev, struct device_driver *drv)
{
    struct wmi_driver *wdrv = to_wmi_driver(drv);
    struct wmi_device *wdev = to_wmi_device(dev);
    const struct wmi_device_id *id;

    id = wdrv->id_table;
    if (!id) return 0;

    while (id->guid_string[0]) {
        if (sysfs_streq(id->guid_string, wdev->guid_string))
            return 1;
        id++;
    }
    return 0;
}
```

Алгоритм обходить масив `id_table` драйвера до порожнього елемента `{}`. Функція `sysfs_streq()` порівнює текстовий рядок `id->guid_string` із рядком `wdev->guid_string` пристрою. Порівняння виконується без урахування регістру символів (case-insensitive) і пропускає символи переведення рядка. Якщо виявлено збіг, шина вважає пристрій та драйвер сумісними і переходить до етапу прив'язки (binding).

### Життєвий цикл пристрою: `.probe()` та `.remove()`

Після успішного зіставлення шина викликає обробник `probe` драйвера:

```c
static int my_wmi_probe(struct wmi_device *wdev, const void *context)
{
    struct my_driver_priv *priv;

    priv = devm_kzalloc(&wdev->dev, sizeof(*priv), GFP_KERNEL);
    if (!priv)
        return -ENOMEM;

    dev_set_drvdata(&wdev->dev, priv);
    priv->wdev = wdev;

    /* Ініціалізація дочірніх підсистем: input, hwmon, sysfs-групи */

    return 0;
}
```

Під час виконання `.probe()` драйвер повинен виконати такі дії:

1. Виділити пам'ять для внутрішньої структури стану пристрою за допомогою керованого ресурсовиділення `devm_kzalloc()`. Це гарантує автоматичне звільнення пам'яті у разі помилки або відв'язки пристрою.
2. Зберегти вказівник на структуру стану в об'єкті пристрою через `dev_set_drvdata(&wdev->dev, priv)`.
3. Отримати приватний контекст `context`, який було вказано в `wmi_device_id`, та використати його для визначення модифікації апаратури.
4. Зареєструвати пристрій у суміжних підсистемах ядра (`input_register_device()`, `hwmon_device_register_with_info()`, `led_classdev_register()`).

При вилученні пристрою або вивантаженні модуля ядра викликається обробник `.remove(struct wmi_device *wdev)`:

```c
static void my_wmi_remove(struct wmi_device *wdev)
{
    struct my_driver_priv *priv = dev_get_drvdata(&wdev->dev);

    /* Скасування реєстрації підсистем та очищення ресурсів */
}
```

Обробник `.remove()` вилучає зареєстровані атрибути sysfs та скасовує реєстрацію дочірніх пристроїв. Оскільки пам'ять виділялася через `devm_kzalloc()`, ядро самостійно звільнить об'єкт `priv` після повернення з `.remove()`.

---

## 3. Механізм асинхронних сповіщень: callback `notify`

Важливим завданням підсистеми WMI є обробка асинхронних апаратних подій (натискання гарячих клавіш Fn, підключення зовнішніх блоків живлення, сповіщення термодатчиків).

### Сигнатура та ланцюг надходження сповіщення

Обробник асинхронних подій реєструється у структурі `struct wmi_driver` через поле `.notify`:

```c
void (*notify)(struct wmi_device *wdev, union acpi_object *data);
```

Повний шлях проходження апаратного сповіщення від фірмваре до callback-функції містить такі етапи:

1. **Генерація ACPI SCI:** Системний контролер (EC) надсилає переривання SCI. Інтерпретатор ACPICA виконує AML-код обробника GPE.
2. **Виконання AML Notify:** AML-код виконує інструкцію `Notify(\_SB.WMI1, event_code)`, де `event_code` є числовим кодом події (наприклад `0x80`).
3. **Перехоплення в `wmi.ko`:** Двопотоковий обробник `wmi.ko` знаходить відповідний запис у `_WDG` з прапорцем `ACPI_WMI_EVENT` (`0x08`), чий notification ID збігається з `event_code`.
4. **Виконання методу `_WED`:** За замовчуванням (якщо прапорець `no_notify_data` у `struct wmi_driver` дорівнює `false`), підсистема `wmi.ko` автоматично викликає AML-метод `_WED(event_code)` (WMI Event Data) для зчитання додаткових деталей події.
5. **Виклик callback `.notify()`:** Результат виконання `_WED` у вигляді об'єкта `union acpi_object` передається другим аргументом у функцію `.notify()` зареєстрованого драйвера.

### Аналіз об'єкта `union acpi_object` та безпечна перевірка типів

Об'єкт `union acpi_object` містить поле `type`, яке визначає формат отриманих даних. Перед читанням даних драйвер зобов'язаний виконати перевірку типу:

```c
static void my_wmi_notify(struct wmi_device *wdev, union acpi_object *data)
{
    struct my_driver_priv *priv = dev_get_drvdata(&wdev->dev);

    if (!data) {
        dev_warn(&wdev->dev, "Отримано порожнє сповіщення WMI\n");
        return;
    }

    switch (data->type) {
    case ACPI_TYPE_INTEGER:
        dev_dbg(&wdev->dev, "Отримано цілочисельну подію WMI: 0x%llx\n",
                data->integer.value);
        my_handle_scancode(priv, (u32)data->integer.value);
        break;

    case ACPI_TYPE_BUFFER:
        dev_dbg(&wdev->dev, "Отримано буфер події WMI довжиною %u байт\n",
                data->buffer.length);
        my_parse_event_buffer(priv, data->buffer.pointer, data->buffer.length);
        break;

    case ACPI_TYPE_PACKAGE:
        dev_dbg(&wdev->dev, "Отримано пакет подій WMI з %u елементів\n",
                data->package.count);
        break;

    default:
        dev_err(&wdev->dev, "Непідтримуваний тип об'єкта події: %u\n", data->type);
        break;
    }
}
```

Нехтування перевіркою `data->type` є поширеною помилкою, яка призводить к збоям ядра (Kernel Null Pointer Dereference) при отриманні нестандартних даних від некоректних версій BIOS.

### Управління пам'яттю та життєвий цикл буфера сповіщення

Пам'ять для об'єкта `union acpi_object *data` виділяється підсистемою ACPICA під час виконання методу `_WED`.

- **Увага:** Драйвер **не повинен** викликати `kfree()` для вказівника `data`, переданого у callback `.notify()`.
- Підсистема `wmi.ko` автоматично звільняє пам'ять об'єкта `data` одразу після повернення з функції `.notify()`.
- Якщо драйверу потрібно передати отримані дані для асинхронної обробки у фоновий поток (`struct work_struct` або `workqueue`), він зобов'язаний створити локальну глибоку копію буфера за допомогою `kmemdup()` або `kstrdup()` і самостійно звільнити її після обробки.

### Інтеграція з підсистемою input ядра

Події `notify` найчастіше використовуються для обробки натискань Fn-клавіш. Для їхньої трансляції драйвери ядра застосовують підсистему `sparse-keymap`:

```c
#include <linux/input/sparse-keymap.h>

static const struct key_entry my_wmi_keymap[] = {
    { KE_KEY, 0x85, { KEY_BRIGHTNESSUP } },
    { KE_KEY, 0x86, { KEY_BRIGHTNESSDOWN } },
    { KE_KEY, 0x87, { KEY_WLAN } },
    { KE_END, 0 }
};

/* У функції .probe(): */
int ret = sparse_keymap_setup(priv->input_dev, my_wmi_keymap, NULL);

/* У функції .notify(): */
if (data && data->type == ACPI_TYPE_INTEGER)
    sparse_keymap_report_event(priv->input_dev, (u32)data->integer.value, 1, true);
```

Функція `sparse_keymap_report_event()` автоматично знаходить скан-код у таблиці маппінгу, генерує події `input_report_key()` та `input_sync()`, транслюючи їх до системного пристрою `/dev/input/eventX`.

---

## 4. Розбір та формат рядків GUID (GUID_STRING)

У підсистемі WMI ідентифікація блоків даних та методів здійснюється через 128-бітні глобально унікальні ідентифікатори (GUID). Однак між бінарним представленням у DSDT та канонічним рядком у C-коді існує важлива різниця.

### Бінарний формат у таблиці `_WDG` vs Канонічний рядок

У двійковому буфері `_WDG` (на рівні DSDT/SSDT) GUID зберігається у вигляді 16 послідовних байтів у формати Mixed-Endian / Little-Endian (згідно зі специфікацією Microsoft WMI та UEFI):

```text
+-------------------+-----------------+-----------------+-------------------------+
| Data1 (4 байти)   | Data2 (2 байти) | Data3 (2 байти) | Data4 (8 байтів)        |
| Little-Endian     | Little-Endian   | Little-Endian   | Big-Endian (Raw Bytes)  |
+-------------------+-----------------+-----------------+-------------------------+
```

Канонічний текстовий рядок GUID (наприклад `"9DBB5994-A997-11DA-B012-B622A1EF5492"`) складається з **36 символів** і розділений чотирма дефісами:
`8-4-4-4-12` hex-символів.

Під час парсингу буфера `_WDG` драйвер ядра `wmi.ko` конвертує бінарні 16 байтів у канонічний текстовий рядок за допомогою внутрішнього форматування. Саме цей канонічний 36-символьний рядок записується у поле `wdev->guid_string` і використовується для побудови шляхів sysfs `/sys/bus/wmi/devices/<GUID_STRING>/`.

### Допоміжні функції та типи ядра (`<linux/uuid.h>`)

Ядро Linux розрізняє два типи 128-бітних ідентифікаторів:

- `guid_t`: GUID у Little-Endian форматі (використовується в WMI, ACPI, UEFI).
- `uuid_t`: UUID у суворо Big-Endian форматі (використовується у мережевих протоколах та файлових системах).

Для роботи з WMI GUID у ядрі призначено тип `guid_t` та відповідні маніпуляційні функції:

```c
#include <linux/uuid.h>

/* Оголошення та ініціалізація бінарного GUID з рядка */
guid_t my_guid;
int ret = guid_parse("9DBB5994-A997-11DA-B012-B622A1EF5492", &my_guid);

/* Порівняння двох бінарних GUID */
if (guid_equal(&guid1, &guid2)) {
    /* GUID збігаються */
}

/* Перевірка на порожній (нульовий) GUID */
if (guid_is_null(&my_guid)) {
    /* GUID складається з усіх нулів */
}

/* Експорт бінарного GUID у буфер */
u8 buffer[16];
export_guid(buffer, &my_guid);
```

Використання бінарного порівняння `guid_equal()` всередині критичних до продуктивності ділянок коду є набагато ефективнішим за порівняння рядків через `strcmp()`.

---

## 5. Публічні функції ядра для виконання WMI-методів

Підсистема ядра Linux надає високорівневе API для виконання методів, читання та запису даних у пристрої WMI без необхідності прямого аналізу АМЛ-коду.

### `wmidev_evaluate_method`
Викликає виконавець ACPI-методу (`WMxx`) для вказаного пристрою WMI.

```c
acpi_status wmidev_evaluate_method(struct wmi_device *wdev,
                                    u8 instance,
                                    u32 method_id,
                                    const struct acpi_buffer *in,
                                    struct acpi_buffer *out);
```
- `wdev`: Вказівник на об'єкт `struct wmi_device`.
- `instance`: Індекс екземпляра блоку даних (від `0` до `instance_count - 1`).
- `method_id`: Числовий ідентифікатор методу (Method ID), визначений специфікацією вендора.
- `in`: Вказівник на структуру `struct acpi_buffer` з вхідними параметрами (або `NULL`).
- `out`: Вказівник на структуру `struct acpi_buffer` для збереження результату (зазвичай використовується значення `ACPI_ALLOCATE_BUFFER`).

Функція повертає статус `acpi_status`. При успішному виконанні повертається `AE_OK`. У разі виникнення помилок в інтерпретаторі АМЛ повертаються коди на кшталт `AE_NOT_FOUND` або `AE_BAD_PARAMETER`.

### `wmidev_block_query`
Виконує запит читання блоку даних (WMI Query, `WQxx`) від WMI-пристрою.

```c
acpi_status wmidev_block_query(struct wmi_device *wdev,
                               u8 instance,
                               struct acpi_buffer *out);
```
Функція повертає буфер даних, згенерований відповідним AML-методом `WQxx`. Пам me'ять для результату виділяється ядром і вимагає обов'язкового звільнення розробником через `kfree(out.pointer)`.

### `wmidev_block_set`
Виконує запит запису блоку даних (WMI Set, `WSxx`) у WMI-пристрій.

```c
acpi_status wmidev_block_set(struct wmi_device *wdev,
                             u8 instance,
                             const struct acpi_buffer *in);
```
Приймає вхідні дані `in` і передає їх відповідно в AML-метод `WSxx` прошивки для зміни налаштувань.

### Легасі-функції (депрекейтне API)

У застарілих версіях ядра Linux (до версії 4.13) використовувалися глобальні процедурні функції без прив'язки до `struct wmi_device`:

- `wmi_evaluate_method(const char *guid, u8 instance, u32 method_id, const struct acpi_buffer *in, struct acpi_buffer *out)`
- `wmi_query_block(const char *guid, u8 instance, struct acpi_buffer *out)`
- `wmi_set_block(const char *guid, u8 instance, const struct acpi_buffer *in)`
- `wmi_install_notify_handler(const char *guid, wmi_notify_handler handler, void *data)`
- `wmi_remove_notify_handler(const char *guid)`

Сучасні розробники повинні утримуватися від використання застарілих процедурних функцій на користь об'єктно-орієнтованих `wmidev_*` API та шинної моделі `struct wmi_driver`.

---

## 6. Крайові випадки (Edge Cases) та складні сценарії

При розробці WMI-драйверів необхідно враховувати специфічні апаратні сценарії та крайові випадки роботи прошивок BIOS.

### 1. Кілька екземплярів пристрою (`instance_count > 1`)

Деякі WMI GUID описують масиви однотипних апаратних вузлів (наприклад, декілька температурних датчиків або кулерів). У цьому випадку параметр `instance_count` у бінарному записі `_WDG` перевищує `1`.

- При виклику `wmidev_evaluate_method()`, `wmidev_block_query()` або `wmidev_block_set()` драйвер передає аргумент `instance` у діапазоні від `0` до `instance_count - 1`.
- Передача значення `instance >= instance_count` призводить до негайного повернення помилки `AE_BAD_PARAMETER` інтерпретатором ACPICA. Драйвер зобов'язаний самостійно виконувати перевірку меж індексу перед викликом API.

### 2. Дублювання GUID у кількох пристроях `PNP0C14`

На складних системних платах (наприклад, у двопроцесорних серверах або ігрових ноутбуках із багатьма контролерами) у просторі імен ACPI може бути присутнім кілька незалежних пристроїв WMI з HID `PNP0C14` (наприклад `\_SB.WMI1`, `\_SB.WMI2`).

Якщо обидва ACPI-пристрої містять однаковий GUID у своїх буферах `_WDG`, підсистема ядра `wmi.ko` створює декілька окремих об'єктів `struct wmi_device`. Щоб уникнути колізій імен у файловій системі sysfs `/sys/bus/wmi/devices/`, ядро додає числовий суфікс до імені каталогу пристрою (наприклад `9DBB5994-A997-11DA-B012-B622A1EF5492-0` та `9DBB5994-A997-11DA-B012-B622A1EF5492-1`).

### 3. Ресурсоємні блоки даних (`ACPI_WMI_EXPENSIVE`, `0x01`)

Якщо в записі `_WDG` встановлено прапорець `ACPI_WMI_EXPENSIVE` (`0x01`), зчитування відповідного блоку даних вимагає суттєвих обчислювальних ресурсів Embedded Controller (наприклад, опитування десятків аналогових сенсорів).

Ядро Linux не опитує такі пристрої у фоновому режимі. Більше того, прошивка BIOS може вимагати явного ввімкнення збору даних через виклик спецметодів до початку опитування та вимкнення після його завершення.

### 4. Текстові блоки даних (`ACPI_WMI_STRING`, `0x04`)

Якщо встановлено прапорець `ACPI_WMI_STRING` (`0x04`), повернений буфер містить текстовий рядок. Однак прошивки BIOS часто повертають рядки у форматі UTF-16LE (UCS-2) із двобайтовим префіксом довжини:

```c
struct acpi_buffer out = { ACPI_ALLOCATE_BUFFER, NULL };
acpi_status status = wmidev_block_query(wdev, 0, &out);

if (ACPI_SUCCESS(status) && out.pointer) {
    union acpi_object *obj = out.pointer;
    if (obj->type == ACPI_TYPE_BUFFER) {
        u16 *utf16_str = (u16 *)obj->buffer.pointer;
        char utf8_buf[256];

        /* Конвертація UTF-16LE у UTF-8 для використання в Linux */
        utf16s_to_utf8s(utf16_str, obj->buffer.length / 2,
                        UTF16_LITTLE_ENDIAN, utf8_buf, sizeof(utf8_buf) - 1);
    }
    kfree(out.pointer);
}
```

Використання функції ядра `utf16s_to_utf8s()` є обов'язаним для коректного відображення текстових системних атрибутів у Linux.

### 5. Динаміка станів живлення (PM Suspend / Resume)

При переході системи в стан сну (S3/S0ix) Embedded Controller може скинути внутрішні конфігураційні регістри. Драйвер WMI зобов'язаний реалізувати збереження та відновлення стану через PM callback:

```c
static int my_wmi_suspend(struct device *dev)
{
    struct my_driver_priv *priv = dev_get_drvdata(dev);
    /* Збереження поточних налаштувань вентиляторів/підсвічування */
    return 0;
}

static int my_wmi_resume(struct device *dev)
{
    struct my_driver_priv *priv = dev_get_drvdata(dev);
    /* Повторне виконання WMI-методів для відновлення стану EC */
    return my_restore_hardware_state(priv);
}

static DEFINE_SIMPLE_DEV_PM_OPS(my_wmi_pm_ops, my_wmi_suspend, my_wmi_resume);
```

---

## 7. Коди статусів, діагностика та обробка помилок

Функції підсистеми WMI повертають статуси типу `acpi_status`, що є цілочисельними макросами підсистеми ACPICA.

### Перелік та аналіз статусів `acpi_status`

| Код макросу `acpi_status` | Числове значення | Семантичний опис помилки |
| :--- | :--- | :--- |
| `AE_OK` | `0x0000` | Операція виконана успішно без помилок. |
| `AE_ERROR` | `0x0001` | Неспецифікована внутрішня помилка підсистеми ACPI. |
| `AE_NO_MEMORY` | `0x0004` | Недостатньо оперативної пам'яті для виділення буферів. |
| `AE_NOT_FOUND` | `0x0005` | Запитаний WMI-метод чи GUID відсутній у прошивці BIOS. |
| `AE_BAD_PARAMETER` | `0x0006` | Передано некоректний вхідний параметр або неспівпадаючий буфер. |
| `AE_TIME` | `0x000E` | Перевищено таймаут очікування відповіді від Embedded Controller. |
| `AE_BUFFER_OVERFLOW` | `0x000F` | Вихідний буфер занадто малий для збереження результату. |

### Конвертація статусів у системні коди POSIX (-ERRNO)

Функції ядра Linux у підсистемах sysfs та VFS вимагають повернення стандартних від'ємних кодів помилок POSIX (наприклад `-EINVAL`, `-ENODEV`). Для маппінгу `acpi_status` використовується така стратегія:

```c
int acpi_status_to_errno(acpi_status status)
{
    switch (status) {
    case AE_OK:
        return 0;
    case AE_NOT_FOUND:
        return -ENODEV;
    case AE_BAD_PARAMETER:
        return -EINVAL;
    case AE_NO_MEMORY:
        return -ENOMEM;
    case AE_TIME:
        return -ETIMEDOUT;
    default:
        return -EIO;
    }
}
```

Використання `acpi_status_to_errno()` гарантує, що системні виклики простору користувача (`read()`, `write()`) отримають зрозумілі коди помилок (`ENODEV`, `ETIMEDOUT`).

### Затримки системного контролера та таймаути (`AE_TIME`)

Команда `wmidev_evaluate_method()` передає запит до Embedded Controller через шину LPC або eSPI. Якщо EC заблокований у режимі виконання іншої операції або не відповідає на переривання, ACPICA перериває виконання за таймаутом і повертає `AE_TIME`.

Драйвер ядра зобов'язаний коректно обробляти статус `AE_TIME`:
- Не повторювати запит у нескінченному циклі без паузи (`msleep()`).
- Фіксувати помилку в системному журналі через `dev_err_ratelimited()`, щоб запобігти заповненню кільцевого буфера `dmesg`.

### Динамічне налагодження (Dynamic Debug)

Для трасування викликів WMI у реальному часі без перекомпіляції ядра використовується механізм `dynamic_debug`:

```bash
# Ввімкнення трасування для модуля wmi
echo "module wmi +p" > /sys/kernel/debug/dynamic_debug/control

# Ввімкнення трасування для конкретного вендорського драйвера
echo "module asus_wmi +p" > /sys/kernel/debug/dynamic_debug/control
```

Після цього всі внутрішні виклики `pr_debug()` та `dev_dbg()` у підсистемі WMI виводитимуться у журнал `dmesg`.

---

## 8. Структура віртуальної файлової системи Sysfs

Підсистема WMI експортує інформацію про виявлені пристрої у простір файлової системи `/sys/bus/wmi/devices/`:

```text
/sys/bus/wmi/devices/
├── 05901221-D566-11D1-B2F0-00A0C9062910/ (Стандартний BMOF GUID)
│   ├── bmof               (Бінарний буфер Managed Object Format для декомпіляції)
│   ├── modalias           (Спеціальний рядок ідентифікації udev: wmi:05901221-...)
│   └── object_id          (Двосимвольний ACPI Object ID, напр. "MO")
├── 97845ED0-4E6D-11DE-8A39-0800200C9A66/ (Вендорський WMI GUID)
│   ├── driver -> ../../../bus/wmi/drivers/asus-wmi (Символьне посилання на драйвер)
│   ├── setable            (Фоновий прапорець: 1 — запис дозволено, 0 — лише читання)
│   └── instance_count     (Кількість екземплярів пристрою в прошивці)
```

Кожен атрибут у системі sysfs безпосередньо відображає відповідне поле з 20-байтового запису `_WDG`. Файл `setable` повертає число `1` тільки якщо GUID підтримує метод `WSxx` або прямий запис у data block. Наявність символьного посилання `driver` підтверджує, що даний GUID успішно прив'язано до завантаженого модуля ядра. Прапорці у файлі `modalias` дозволяють демону `udevd` здійснювати гаряче завантаження відповідних модулів ядра при виявленні нових апаратних GUID. 

Приклад генерації правила udev для автозавантаження драйвера за модаліасом WMI:

```udev
ACTION=="add", SUBSYSTEM=="wmi", MODALIAS=="wmi:9DBB5994-A997-11DA-B012-B622A1EF5492", RUN+="/sbin/modprobe dell-wmi"
```

---

## 9. Підсумок

Розроблений у ядрі Linux API для підсистеми ACPI-WMI надає надійну абстракцію над специфічними функціями прошивок BIOS. Використання шинної модели `wmi_bus_type`, декларативної реєстрації `struct wmi_driver` та сучасних методів `wmidev_evaluate_method()` дозволяє створювати безпечні, ресурсо-ефективні драйвери обладнання, що гармонійно інтегруються у загальну систему Linux Device Model.
