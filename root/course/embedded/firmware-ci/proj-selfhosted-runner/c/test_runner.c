// test_runner.c — прошивка стенда в режимі on-target тестів.
// Збирається ТИМ САМИМ крос-тулчейном, що й бойова прошивка, але з -DHIL_TEST:
// у main() замість бойового циклу — банер, тести, вердикт.

#include <stdint.h>
#include "uart.h"      // ваш драйвер UART: uart_init(), uart_puts()

// Контракт із раннером. Ці три префікси — увесь «протокол» стенда.
#define HIL_BANNER  "HIL-READY v1"     // «я ожив» одразу після старту
#define HIL_PASS    "RESULT: PASS"     // усе зелено
#define HIL_FAIL    "RESULT: FAIL "    // за префіксом — число провалів

// Лічильники набігають протягом прогону; наприкінці стають вердиктом.
static uint32_t tests_run    = 0;
static uint32_t tests_failed = 0;
