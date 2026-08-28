#include <kunit/test.h>

/* Тіло окремого тесту */
static void test_example_addition(struct kunit *test)
{
	int sum = 2 + 2;
	KUNIT_EXPECT_EQ(test, sum, 4);
}

/* Опис списку тестів у сюїті */
static struct kunit_case example_test_cases[] = {
	KUNIT_CASE(test_example_addition),
	{} /* Фінальний порожній елемент-маркер */
};

/* Опис тестового сюїту */
static struct kunit_suite example_test_suite = {
	.name = "example_addition_suite",
	.test_cases = example_test_cases,
};

/* Реєстрація сюїту в системі */
kunit_test_suite(example_test_suite);
