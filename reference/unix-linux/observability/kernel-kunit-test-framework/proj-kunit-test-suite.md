# ⚙️ Практична реалізація тестового сюїту KUnit з підвохами санітайзерів

Практична реалізація тестового сюїту KUnit для модуля ядра Linux, що містить кільцевий буфер даних. У цій вставці покроково розібрано архітектуру тестування у просторі ядра, використання автоматичного управління ресурсами через `kunit_kzalloc()`, застосування фатальних та нефатальних тверджень, а також сценарії виявлення помилок адресації відлагоджувачами KASAN та KFENCE.

## 1. Постановка інженерної задачі та архітектура компонента

Кільцевий буфер (Ring Buffer або Circular FIFO) є фундаментальною структурою даних у ядрі Linux. Він застосовується у драйверах мережевих карт, підсистемах обробки системних журналів (`printk`), драйверах блокових пристроїв та драйверах вводу-виводу для передачі даних між контекстами переривань (Interrupt Context) та потоками виконання ядра (Kernel Threads).

Помилка у розрахунку індексів головки (`head`) чи хвоста (`tail`) кільцевого буфера або відсутність перевірки переповнення призводить до важких системних аварій: перезапису суміжних блоків пам'яті ядра, виходу за межі виділеної області (Slab Out-of-Bounds) або руйнування метаданих аллокатора `kmalloc`.

Для забезпечення надійності розробляється модуль ядра, що містить кільцевий буфер фіксованого розміру `struct kunit_ring_buffer` із захистом критичних секцій за допомогою спін-блокувань `spinlock_t`.

### Програмний contract кільцевого буфера

Компонент надає три основні операції:
1. `ring_buf_create()`: Створення та ініціалізація структури буфера із виділенням динамічної пам'яті.
2. `ring_buf_push()`: Додавання одного байта у хвіст буфера із перевіркою переповнення (`-ENOSPC`).
3. `ring_buf_pop()`: Вилучення одного байта з голови буфера із перевіркою порожнечі (`-ENODATA`).

Тестовий сюїт KUnit повинен гарантувати:
- Коректність порядкового зберігання елементів (First-In, First-Out).
- Точність обліку кількості елементів (`count`).
- Правильність обробки крайових умов (повний та порожній буфер).
- Відсутність витоків пам'яті при виникненні помилок у ході тестування.

---

## 2. Реалізація вихідного коду модуля ядра та KUnit-тестів

Нижче наведено повний вихідний код модуля ядра `kunit_ring_buffer_test.c`, який включає реалізацію кільцевого буфера та тестовий сюїт KUnit.

```c
// SPDX-License-Identifier: GPL-2.0
/*
 * Модуль ядра Linux: KUnit тестовий сюїт для кільцевого буфера.
 */

#include <kunit/test.h>
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/spinlock.h>

/* --- 1. Реалізація тестируемого компонента --- */

struct kunit_ring_buffer {
	u8 *buffer;
	size_t capacity;
	size_t head;
	size_t tail;
	size_t count;
	spinlock_t lock;
};

static struct kunit_ring_buffer *ring_buf_create(struct kunit *test, size_t capacity)
{
	struct kunit_ring_buffer *rb;

	/*
	 * Використовуємо kunit_kzalloc замість стандартного kzalloc:
	 * Виділена пам'ять прив'язується до контексту struct kunit *test.
	 * При завершенні тесту (успішному або через KUNIT_ASSERT) KUnit
	 * гарантовано вивільнить цей блок пам'яті, запобігаючи витокам.
	 */
	rb = kunit_kzalloc(test, sizeof(*rb), GFP_KERNEL);
	KUNIT_ASSERT_NOT_NULL(test, rb);

	rb->buffer = kunit_kzalloc(test, capacity, GFP_KERNEL);
	KUNIT_ASSERT_NOT_NULL(test, rb->buffer);

	rb->capacity = capacity;
	rb->head = 0;
	rb->tail = 0;
	rb->count = 0;
	spin_lock_init(&rb->lock);

	return rb;
}

static int ring_buf_push(struct kunit_ring_buffer *rb, u8 val)
{
	unsigned long flags;

	spin_lock_irqsave(&rb->lock, flags);

	if (rb->count >= rb->capacity) {
		spin_unlock_irqrestore(&rb->lock, flags);
		return -ENOSPC;
	}

	rb->buffer[rb->head] = val;
	rb->head = (rb->head + 1) % rb->capacity;
	rb->count++;

	spin_unlock_irqrestore(&rb->lock, flags);
	return 0;
}

static int ring_buf_pop(struct kunit_ring_buffer *rb, u8 *val)
{
	unsigned long flags;

	spin_lock_irqsave(&rb->lock, flags);

	if (rb->count == 0) {
		spin_unlock_irqrestore(&rb->lock, flags);
		return -ENODATA;
	}

	*val = rb->buffer[rb->tail];
	rb->tail = (rb->tail + 1) % rb->capacity;
	rb->count--;

	spin_unlock_irqrestore(&rb->lock, flags);
	return 0;
}

/* --- 2. Тестові сценарії KUnit --- */

/* Сценарій 1: Базова ініціалізація та збереження порядку FIFO */
static void test_ring_buf_basic_fifo(struct kunit *test)
{
	struct kunit_ring_buffer *rb;
	u8 val = 0;

	rb = ring_buf_create(test, 4);

	KUNIT_EXPECT_EQ(test, rb->count, (size_t)0);

	KUNIT_EXPECT_EQ(test, ring_buf_push(rb, 0xAA), 0);
	KUNIT_EXPECT_EQ(test, ring_buf_push(rb, 0xBB), 0);
	KUNIT_EXPECT_EQ(test, rb->count, (size_t)2);

	KUNIT_EXPECT_EQ(test, ring_buf_pop(rb, &val), 0);
	KUNIT_EXPECT_EQ(test, val, (u8)0xAA);

	KUNIT_EXPECT_EQ(test, ring_buf_pop(rb, &val), 0);
	KUNIT_EXPECT_EQ(test, val, (u8)0xBB);

	KUNIT_EXPECT_EQ(test, rb->count, (size_t)0);
}

/* Сценарій 2: Перевірка граничних станів (переповнення та опустошення) */
static void test_ring_buf_overflow(struct kunit *test)
{
	struct kunit_ring_buffer *rb;
	u8 val = 0;

	rb = ring_buf_create(test, 2);

	KUNIT_EXPECT_EQ(test, ring_buf_push(rb, 1), 0);
	KUNIT_EXPECT_EQ(test, ring_buf_push(rb, 2), 0);

	/* Спроба третього push повинна повернути помилку -ENOSPC */
	KUNIT_EXPECT_EQ(test, ring_buf_push(rb, 3), -ENOSPC);
	KUNIT_EXPECT_EQ(test, rb->count, (size_t)2);

	KUNIT_EXPECT_EQ(test, ring_buf_pop(rb, &val), 0);
	KUNIT_EXPECT_EQ(test, ring_buf_pop(rb, &val), 0);

	/* Порожній буфер повинен повернути помилку -ENODATA */
	KUNIT_EXPECT_EQ(test, ring_buf_pop(rb, &val), -ENODATA);
}

/* Сценарій 3: Інтеграція з KASAN/KFENCE для виявлення помилок адресації */
static void test_ring_buf_kasan_oob_demo(struct kunit *test)
{
	struct kunit_ring_buffer *rb;
	u8 *raw_ptr;

	rb = ring_buf_create(test, 8);
	raw_ptr = rb->buffer;

	/*
	 * Для перевірки спрацювання KASAN розкоментуйте наступний рядок.
	 * Запис за індексом 8 виходить за межі масиву з 8 елементів (індекси 0..7).
	 * KASAN виявить факт Out-of-Bounds запису у тіньовій пам'яті (Redzone)
	 * і зґенерує трасування стеку vmlinux у dmesg.
	 */
	// raw_ptr[8] = 0xFF;

	KUNIT_EXPECT_NOT_NULL(test, raw_ptr);
}

/* --- 3. Оголошення та реєстрація тестового сюїту --- */

static struct kunit_case ring_buf_test_cases[] = {
	KUNIT_CASE(test_ring_buf_basic_fifo),
	KUNIT_CASE(test_ring_buf_overflow),
	KUNIT_CASE(test_ring_buf_kasan_oob_demo),
	{}
};

static struct kunit_suite ring_buf_test_suite = {
	.name = "kunit_ring_buffer_suite",
	.test_cases = ring_buf_test_cases,
};

kunit_test_suite(ring_buf_test_suite);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("KUnit Test Suite for Ring Buffer with Sanitizer Support");
```

---

## 3. Детальний аналіз ключових рішень та механізмів KUnit у коді

Для глибокого розуміння представленого коду розглянемо основні архітектурні прийоми та потенційні пастки при написанні KUnit-тестів у ядрі.

### 3.1. Управління пам'яттю та автоочищення (`kunit_kzalloc`)

У функції `ring_buf_create()` виділення пам'яті відбувається за допомогою виклику `kunit_kzalloc(test, ...)`. Цей виклик є важливою відмінністю KUnit від стандартного програмування модулів ядра.

При використанні звичайного `kzalloc()` розробник зобов'язаний самостійно викликами `kfree()` вивільняти пам'ять у кожному тестовому випадку. Проте, якщо всередині тесту спрацьовує фатальне твердження `KUNIT_ASSERT_EQ()`, KUnit негайно перериває виконання функції тесту через `longjmp` або внутрішню зупинку потоку тесту. Усі лінії коду `kfree()`, що розташовані нижче точки збою, пропускаються, створюючи неминучий виток пам'яті.

`kunit_kzalloc()` розв'язує цю проблему: він реєструє виділений блок пам'яті у внутрішній структурі ресурсів `test->resources`. Незалежно від того, як саме завершився тест (успішно, через `KUNIT_EXPECT_FAIL`, чи аварійно через `KUNIT_ASSERT`), підсистема очищення KUnit автоматично звільнить усю виділену пам'ять.

### 3.2. Вибір між фатальними та нефатальними перевірками

У функції `ring_buf_create()` для перевірки результату виділення пам'яті застосовано макрос `KUNIT_ASSERT_NOT_NULL(test, rb)`. Використання фатальної перевірки `ASSERT` тут є єдино правильним рішенням: якщо аллокатор пам'яті ядра з якихось причин повернув `NULL`, подальші спроби звернення до полів `rb->capacity` або `rb->head` у наступних рядках призведуть до `null-pointer dereference` та краху ядра (`kernel panic`). Фатальне твердження негайно зупиняє виконання тесту і запобігає краху всієї системи.

Натомість у тестових сценаріях `test_ring_buf_basic_fifo` використано нефатальні макроси `KUNIT_EXPECT_EQ()`. Якщо перший запис поверне помилку, KUnit зафіксує цей факт, але дозволить тесту виконати наступні перевірки. Це дає розробнику можливість побачити повну картину стану буфера у звіті TAP.

### 3.3. Блокування спін-локами (`spinlock_t`) та взаємодія з санітайзерами

Реалізація кільцевого буфера використовує `spin_lock_irqsave()`. Захист критичної секції є обов'язковим для коду ядра, оскільки додавання або вилучення даних може викликатися з контексту апаратного переривання (ISR).

При виконанні цього тесту під управлінням **KCSAN (Kernel Concurrency Sanitizer)** санітайзер відстежує стан критичної секції. Якщо прибрати виклики `spin_lock_irqsave` і запустити паралельне виконання `ring_buf_push()` із декількох тестових потоків, KCSAN миттєво виявить факт несинхронізованого запису в `rb->buffer[rb->head]` та попередить про наявність стану гонитви (Data Race).

У разі увімкненого **KASAN** спроба зчитати елемент поза межами виділеного розміру (наприклад, `raw_ptr[8]` при розмірі буфера 8) призведе до того, що KASAN зчитає заотруєний байт тіньової пам'яті (Shadow Memory) і заблокує операцію з виводом такого звіту у `dmesg`:

```text
==================================================================
BUG: KASAN: slab-out-of-bounds in test_ring_buf_kasan_oob_demo+0x42/0x70
Write of size 1 at addr ffff888102345678 by task kunit_try_catch/142
CPU: 1 PID: 142 Comm: kunit_try_catch Tainted: G        W          6.1.0 #1
Call Trace:
 <TASK>
 kasan_report+0xab/0xe0
 test_ring_buf_kasan_oob_demo+0x42/0x70
 kunit_generic_run_threadfn_adapter+0x28/0x40
 ...
==================================================================
```

---

## 4. Конфігурація збірки та інструкції запуск тесту

Для інтеграції створеного тестового модуля у вихідне дерево ядра Linux виконуються такі кроки конфігурації.

### 4.1. Створення конфігураційного файла `.kunitconfig`

У корені тестового каталогу або в дереві ядра створюється мінімальний конфігураційний файл `.kunitconfig`, який описує потрібні опції ядра:

```text
CONFIG_KUNIT=y
CONFIG_KUNIT_ALL_TESTS=y
CONFIG_KASAN=y
CONFIG_KASAN_INLINE=y
CONFIG_LOCKDEP=y
```

### 4.2. Створення файлів Kconfig та Makefile

У відповідному каталозі ядра (наприклад, `drivers/char/`) додається оголошення у `Kconfig`:

```text
config RING_BUFFER_KUNIT_TEST
	tristate "KUnit test for Lockfree Ring Buffer" if BURNT_TESTS
	depends on KUNIT
	default KUNIT_ALL_TESTS
	help
	  This builds the KUnit test suite for the lockfree ring buffer.
	  If unsure, say N.
```

Та відповідний рядок у `Makefile`:

```makefile
obj-$(CONFIG_RING_BUFFER_KUNIT_TEST) += kunit_ring_buffer_test.o
```

### 4.3. Запуск у середовищі User Mode Linux (UML)

Запуск тестового сюїту виконується однією командою із кореневого каталогу вихідного коду ядра:

```bash
./tools/testing/kunit/kunit.py run --kunitconfig=drivers/char/.kunitconfig
```

Результатом виконання буде збірка UML-ядра, його автоматичний запуск у фоновому режимі, виконання усіх тестових випадків сюїту `kunit_ring_buffer_suite` та підсумковий кольоровий звіт про проходження тестів у терміналі.
