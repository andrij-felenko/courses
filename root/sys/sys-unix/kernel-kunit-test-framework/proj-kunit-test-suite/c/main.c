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
