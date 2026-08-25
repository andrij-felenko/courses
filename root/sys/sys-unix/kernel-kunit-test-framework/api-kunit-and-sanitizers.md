# 📋 Інтерфейс API KUnit та налаштування санітайзерів

Системне довідкове керівництво по інтерфейсу програмування (API) фреймворку KUnit, макросам тверджень, підсистемі управління ресурсами, динамічним заглушкам, а також параметрам завантаження та викликам sysfs/debugfs для відлагоджувачів KASAN, KCSAN та KFENCE.

## 1. Структури даних та макроси оголошення тестів KUnit

Для створення тестового сюїту в просторі ядра використовуються базові структури даних `struct kunit_case` та `struct kunit_suite`, визначені у заголовочному файлі `<kunit/test.h>`.

### Специфікація фундаментальних структур KUnit

Кожен окремий тестовий сценарій представлений екземпляром структури `struct kunit_case`. Набір пов'язаних тестових сценаріїв об'єднується в `struct kunit_suite`.

### Таблиця 1. Основні структури даних KUnit

| Структура / Поле | Тип | Опис та призначення |
| :--- | :--- | :--- |
| `struct kunit_case` | `struct` | Описує один окремий тестовий сценарій (Test Case). |
| `.run_case` | `void (*)(struct kunit *)` | Вказівник на функцію, що містить тіло тесту. |
| `.name` | `const char *` | Текстове ім'я тесту для виводу у протокол TAP. |
| `.generate_params` | `const void *(*)(const void *, char *)` | Функція генерації параметрів для табличних тестів (`KUNIT_CASE_PARAM`). |
| `.attr` | `struct kunit_attributes` | Метадані та атрибути тесту (наприклад, швидкість чи вимога до HW). |
| `struct kunit_suite` | `struct` | Набір (Suite), що об'єднує групу пов'язаних тестових сценаріїв. |
| `.name` | `const char *` | Унікальна назва тестового сюїту (використовується у логах та TAP). |
| `.init` | `int (*)(struct kunit *)` | Функція ініціалізації перед виконанням *кожного* тесту в сюїті (Set Up). |
| `.exit` | `void (*)(struct kunit *)` | Функція очищення після виконання *кожного* тесту в сюїті (Tear Down). |
| `.suite_init` | `int (*)(struct kunit_suite *)` | Одноразова ініціалізація перед запуском *усього* сюїту. |
| `.suite_exit` | `void (*)(struct kunit_suite *)` | Одноразове очищення після завершення *усього* сюїту. |
| `.test_cases` | `struct kunit_case *` | Масив тестових випадків, що завершується порожнім елементом `{}`. |

### Опис макросів реєстрації сюїтів

- `KUNIT_CASE(test_name)` — макрос для ініціалізації елемента `struct kunit_case` за іменем функції. Приймає назву функції C з сигнатурою `void fn(struct kunit *test)`.
- `KUNIT_CASE_PARAM(test_name, gen_func)` — оголошення параметризованого тесту (table-driven test). Функція `gen_func` генерує послідовність параметрів, за якими тестова функція `test_name` викликається кілька разів поспіль з різними вхідними даними.
- `KUNIT_ARRAY_PARAM(name, array, get_desc)` — допоміжний макрос для створення генератора параметрів `gen_func` на основі статичного масиву C.
- `kunit_test_suite(suite_struct)` — реєструє одиночний сюїт ядра. Створює відповідну макроструктуру для зв'язування з ELF-секцією `.kunit_test_suites`. Під час компіляції модуля створює функції `init_module` та `cleanup_module` для підтримки завантаження через `insmod`.
- `kunit_test_suites(&suite1, &suite2, ...)` — реєструє список із декількох сюїтів в одному вихідному файлі модуля ядра.

---

## 2. Макроси перевірки та тверджень (Assertions & Expectations)

Фреймворк KUnit розділяє макроси перевірки на дві категорії:
1. **`KUNIT_EXPECT_*` (Нефатальні перевірки)**: Якщо умова не виконується, KUnit фіксує помилку в протоколі тесту, але продовжує виконання поточної функції тесту.
2. **`KUNIT_ASSERT_*` (Фатальні твердження)**: Якщо умова не виконується, KUnit фіксує помилку і негайно перериває виконання поточного тесту (через механізм перехоплення контексту ядра або зупинки потоку тесту).

### Таблиця 2. Специфікація макросів KUNIT_EXPECT_* та KUNIT_ASSERT_*

| Макрос Expectation | Фатальний аналог Assertion | Семантика перевірки |
| :--- | :--- | :--- |
| `KUNIT_EXPECT_EQ(test, left, right)` | `KUNIT_ASSERT_EQ(test, left, right)` | Перевіряє рівність `left == right`. |
| `KUNIT_EXPECT_NE(test, left, right)` | `KUNIT_ASSERT_NE(test, left, right)` | Перевіряє нерівність `left != right`. |
| `KUNIT_EXPECT_LT(test, left, right)` | `KUNIT_ASSERT_LT(test, left, right)` | Перевіряє `left < right`. |
| `KUNIT_EXPECT_LE(test, left, right)` | `KUNIT_ASSERT_LE(test, left, right)` | Перевіряє `left <= right`. |
| `KUNIT_EXPECT_GT(test, left, right)` | `KUNIT_ASSERT_GT(test, left, right)` | Перевіряє `left > right`. |
| `KUNIT_EXPECT_GE(test, left, right)` | `KUNIT_ASSERT_GE(test, left, right)` | Перевіряє `left >= right`. |
| `KUNIT_EXPECT_TRUE(test, condition)` | `KUNIT_ASSERT_TRUE(test, condition)` | Перевіряє, що `condition` обчислюється в `true` (не нуль). |
| `KUNIT_EXPECT_FALSE(test, condition)` | `KUNIT_ASSERT_FALSE(test, condition)` | Перевіряє, що `condition` обчислюється в `false` (нуль). |
| `KUNIT_EXPECT_NULL(test, ptr)` | `KUNIT_ASSERT_NULL(test, ptr)` | Перевіряє `ptr == NULL`. |
| `KUNIT_EXPECT_NOT_NULL(test, ptr)` | `KUNIT_ASSERT_NOT_NULL(test, ptr)` | Перевіряє `ptr != NULL`. |
| `KUNIT_EXPECT_PTR_EQ(test, left, right)`| `KUNIT_ASSERT_PTR_EQ(test, left, right)`| Порівнює два вказівники як адреси пам'яті. |
| `KUNIT_EXPECT_STREQ(test, left, right)` | `KUNIT_ASSERT_STREQ(test, left, right)` | Порівнює C-рядки через `strcmp(left, right) == 0`. |
| `KUNIT_EXPECT_STRNEQ(test, left, right)`| `KUNIT_ASSERT_STRNEQ(test, left, right)`| Перевіряє `strcmp(left, right) != 0`. |
| `KUNIT_EXPECT_MEMEQ(test, left, right, size)` | `KUNIT_ASSERT_MEMEQ(test, left, right, size)` | Порівнює буфери пам'яті довжиною `size` через `memcmp`. |
| `KUNIT_EXPECT_NOT_ERR_OR_NULL(test, ptr)` | `KUNIT_ASSERT_NOT_ERR_OR_NULL(test, ptr)` | Перевіряє, що вказівник не є `NULL` і не містить помилку `IS_ERR()`. |
| `KUNIT_EXPECT_NULL_OR_ERR_PTR(test, ptr)` | `KUNIT_ASSERT_NULL_OR_ERR_PTR(test, ptr)` | Перевіряє, що вказівник є `NULL` або закодований кодом помилки `PTR_ERR()`. |

Усі макроси приймають першим аргументом вказівник на контекст тесту `struct kunit *test`. Крім того, наявні розширені формати з підтримкою кастомного форматованого повідомлення помилки:

```c
KUNIT_EXPECT_EQ_MSG(test, left, right, fmt, ...);
KUNIT_ASSERT_TRUE_MSG(test, condition, fmt, ...);
```

Спеціальний макрос `KUNIT_FAIL(test, fmt, ...)` дозволяє безумовно позначати тест як невдалий із виводом сформованого рядка повідомлення.

---

## 3. Управління ресурсами у KUnit (Resource Management API)

Для запобігання витокам пам'яті та ресурсів при передчасному завершенні тесту KUnit надає кероване середовище виділення ресурсів, що прив'язане до життєвого циклу `struct kunit`.

### Основні функції виділення пам'яті та їх характеристики

- `void *kunit_kmalloc(struct kunit *test, size_t size, gfp_t gfp)`  
  Виділяє блок пам'яті розміром `size` через підсистему `kmalloc()`. Пам'ять автоматично звільняється після завершення поточного тесту, навіть якщо тест викликав `KUNIT_FAIL()` або `KUNIT_ASSERT_*`.
- `void *kunit_kzalloc(struct kunit *test, size_t size, gfp_t gfp)`  
  Аналог `kunit_kmalloc`, що гарантовано обнуляє виділений блок пам'яті.
- `void kunit_kfree(struct kunit *test, const void *ptr)`  
  Явне дострокове звільнення пам'яті, виділеної через `kunit_kmalloc`. Вилучає відповідний запис зі списку ресурсів `test->resources`.
- `void *kunit_kcalloc(struct kunit *test, size_t n, size_t size, gfp_t gfp)`  
  Виділення масиву з `n` елементів розміром `size` із обнуленням пам'яті.

### Кастомні ресурси (`kunit_alloc_resource`)

Для управління складними ресурсами ядра (структури файлових систем, відкриті блоки пристроїв, списки lock, м'ютекси, карти пам'яті) використовується універсальне API ресурсів:

```c
struct kunit_resource *kunit_alloc_resource(
    struct kunit *test,
    kunit_resource_init_t init,
    kunit_resource_free_t free,
    gfp_t gfp,
    void *context
);
```

#### Параметри та сигнатури типів:
- `init`: Сигнатура `int (*)(struct kunit_resource *res, void *context)`. Покликана ініціалізувати поле `res->data` на основі переданого контексту.
- `free`: Сигнатура `void (*)(struct kunit_resource *res)`. Покликана вивільнити виділений ресурс (наприклад, викликати `mutex_destroy` або `iounmap`) при завершенні тесту.
- `gfp`: Прапорці виділення пам'яті аллокатора ядра (`GFP_KERNEL`, `GFP_ATOMIC`).
- `context`: Довільний вказівник на дані, що передаються у функцію `init`.

Усі виділені ресурси зберігаються у двозв'язному списку `test->resources` і звільняються у зворотному порядку їх створення (LIFO — Last-In, First-Out).

---

## 4. Динамічні заглушки та стабілізація тестів (Static Stubbing API)

KUnit надає інфраструктуру перезапису викликів статичних або глобальних функцій (Static Stubbing) без потреби використання C++ підсистем vtable чи важких фреймворків макетування.

### Специфікація API заглушок

- `KUNIT_DEFINE_ACTION_WRAPPER(wrapper_name, real_fn, return_type)`  
  Створює обгортку дії для активації заглушки.
- `void kunit_activate_static_stub(struct kunit *test, void *real_fn, void *replacement_fn)`  
  Перенаправляє усі подальші виклики функції `real_fn` на тестову альтернативу `replacement_fn` в межах виконання поточного тесту `test`.
- `void kunit_deactivate_static_stub(struct kunit *test, void *real_fn)`  
  Відновлює оригінальну поведінку виклику `real_fn`.

У тілі реальної функції для підтримки заглушок використовується макрос перехоплення:

```c
KUNIT_STATIC_STUB_REDIRECT(real_fn, arg1, arg2);
```

Якщо для `real_fn` було активовано заглушку через `kunit_activate_static_stub`, макрос перехоплює потік виконання, викликає `replacement_fn` і виконує негайне повернення з функції `real_fn`.

---

## 5. Конфігураційні параметри ядра та інтерфейси sysfs/debugfs відлагоджувачів

Санітайзери KASAN, KCSAN та KFENCE налаштовуються як під час збірки ядра (`Kconfig`), так і через параметри командного рядка завантаження ядра (kernel command line) або віртуальну файлову систему `debugfs`.

### 5.1. KASAN (Kernel Address Sanitizer)

#### Ключові опції збірки ядра (`Kconfig`):
- `CONFIG_KASAN=y`: Головне увімкнення підсистеми KASAN.
- `CONFIG_KASAN_GENERIC=y`: Класичний режим Software KASAN з інструментацією компілятором.
- `CONFIG_KASAN_SW_TAGS=y`: Режим Software Tag-Based KASAN (для ARM64).
- `CONFIG_KASAN_HW_TAGS=y`: Апаратний режим Hardware Tag-Based KASAN (ARM64 Memory Tagging Extension, MTE).

#### Параметри завантаження ядра (`bootargs`):
- `kasan.mode=sync | async | asym`  
  - `sync`: Синхронний режим (за замовчуванням для Generic/Software KASAN). Виклик `panic()` або генерація звіту негайно при виявленні помилки.
  - `async`: Асинхронний режим (для Hardware Tag-Based KASAN на ARM64). Зменшує накладні витрати, але звіт ґенерується із затримкою.
  - `asym`: Асиметричний режим. Читання перевіряються асинхронно, записи — синхронно.
- `kasan.fault=report | panic`  
  Визначає реакцію ядра на виявлену помилку пам'яті: вивід звіту у `dmesg` чи негайний `panic()`.
- `kasan.stack=on | off`  
  Вмикає або вимикає перевірку виходу за межі стек-фреймів.

---

### 5.2. KCSAN (Kernel Concurrency Sanitizer)

#### Ключові опції збірки ядра (`Kconfig`):
- `CONFIG_KCSAN=y`: Активація інструментації KCSAN.
- `CONFIG_KCSAN_VERBOSE=y`: Додає розширений аналіз стеку викликів при виявленні Data Race.
- `CONFIG_KCSAN_STRICT=y`: Вмикає сувору перевірку для всіх операцій читання/запису.

#### Параметри завантаження ядра (`bootargs`):
- `kcsan.ignore_atomics=0 | 1`  
  Якщо встановлено в `1`, KCSAN ігнорує атомарні операції (`READ_ONCE`, `WRITE_ONCE`, `atomic_read`), фокусуючись лише на незахищених образах пам'яті.
- `kcsan.udev=0 | 1`  
  Увімкнення розширеного моніторингу для драйверів пристроїв.
- `kcsan.report_once_per_type=0 | 1`  
  Пригнічує повторні звіти про той самий тип стану гонитви для уникнення зашумлення журналу `dmesg`.

#### Інтерфейс debugfs:
- `/sys/kernel/debug/kcsan`  
  - `echo on > /sys/kernel/debug/kcsan` — динамічна активація інструментації KCSAN.
  - `echo off > /sys/kernel/debug/kcsan` — деактивація інструментації.
  - `cat /sys/kernel/debug/kcsan` — перегляд статистики зафіксованих race conditions.

---

### 5.3. KFENCE (Kernel Electric-Fence)

#### Ключові опції збірки ядра (`Kconfig`):
- `CONFIG_KFENCE=y`: Головне увімкнення підсистеми KFENCE.
- `CONFIG_KFENCE_SAMPLE_INTERVAL=100`: Значення інтервалу вибірки за замовчуванням (у мс).
- `CONFIG_KFENCE_NUM_OBJECTS=255`: Розмір пулу об'єктів KFENCE.

#### Параметри завантаження ядра (`bootargs`):
- `kfence.sample_interval=N`  
  Інтервал вибірки у мілісекундах. Значення `0` вимикає KFENCE. Значення за замовчуванням — `100` ms (для продакшну). Для агресивного тестування у CI встановлюється значення `1`..`10` ms.
- `kfence.pool_size=P`  
  Кількість виділених захисних сторінок пам'яті (Object Pool). За замовчуванням `255` об'єктів.
- `kfence.deferrable=0 | 1`  
  Використання таймерів, що можуть відкладатися для енергозбереження.

#### Інтерфейс debugfs:
- `/sys/kernel/debug/kfence/stats`  
  Виводить лічильники роботи KFENCE:
  - `enabled`: статус підсистеми (1/0).
  - `allocations`: загальна кількість виділених об'єктів KFENCE.
  - `allocated_bytes`: обсяг виділеної пам'яті.
  - `freed_bytes`: обсяг вивільненої пам'яті.
  - `allocation_failures`: кількість відмов через вичерпання пулу.
  - `total_errors`: загальна кількість виявлених помилок пам'яті.
- `/sys/kernel/debug/kfence/objects`  
  Містить список поточних виділених об'єктів KFENCE із зазначенням адрес захисних сторінок `PROT_NONE` та стеками викликів їх виділення.

---

## 6. Формат виводу результатів TAP 14 (Test Anything Protocol)

KUnit транслює результати виконання тестів у стандартному текстовому форматі TAP версії 14 (Test Anything Protocol v14).

### Приклад виводу KUnit у форматі TAP 14:

```text
TAP version 14
1..1
    # Subtest: ring_buffer_test
    1..3
    ok 1 - test_enqueue_dequeue_ok
    # test_overflow: EXPECTATION FAILED at drivers/char/example_kunit.c:42
    Expected buf->count == 0, but is 1
    not ok 2 - test_overflow
    ok 3 - test_kfence_boundary_check
# ring_buffer_test: pass:2 fail:1 skip:0 total:3
not ok 1 - ring_buffer_test
```

Усі рядки діагностики починаються з символу `#`. CI-пайплайни аналізують цей текстовий потік через `kunit.py` і конвертують його у формати JUnit XML або HTML-звіти.
