// test/test_clamp.c — Unity-тест, який Ceedling збере під x86 і запустить
#include "unity.h"
#include "clamp.h"

void setUp(void)    { }   // викликається перед кожним тестом
void tearDown(void) { }   // і після кожного

void test_clamp_passes_value_in_range(void) {
    TEST_ASSERT_EQUAL_INT16(50, clamp_i16(50, -100, 100));
}

void test_clamp_saturates_below(void) {
    TEST_ASSERT_EQUAL_INT16(-100, clamp_i16(-200, -100, 100));
}

void test_clamp_saturates_above(void) {
    TEST_ASSERT_EQUAL_INT16(100, clamp_i16(200, -100, 100));
}

void test_clamp_handles_equal_bounds(void) {
    TEST_ASSERT_EQUAL_INT16(7, clamp_i16(7, 7, 7));
}
