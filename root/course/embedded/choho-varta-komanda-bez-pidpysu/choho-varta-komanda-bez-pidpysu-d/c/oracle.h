#ifndef ORACLE_H
#define ORACLE_H

#include <stddef.h>
#include <stdint.h>

/* Довжина тегу автентичності: повний HMAC-SHA256. */
#define TAG_LEN 32

/* Як приймач звіряє тег кадру. */
typedef enum {
    ORACLE_NAIVE = 0,         /* memcmp: вихід на першому незбігу */
    ORACLE_CONSTANT_TIME = 1  /* ct_verify: завжди всі TAG_LEN байтів */
} oracle_mode;

/*
 * Модель приймача очима нападника.
 *
 * На столі нападник має дві речі: двійкову відповідь «кадр прийнято чи ні»
 * і ЧАС, за який приймач цю відповідь дав (голка осцилографа на лінії
 * живлення, сплеск струму, затримка відповіді по шині). Час ми моделюємо
 * кількістю фактично зчитаних байтів тегу — це і є та величина, яка витікає
 * з наївного порівняння. Плюс джитер вимірювання: чистих чисел на живому
 * стенді не буває, і нападнику доводиться усереднювати.
 */
typedef struct {
    uint8_t     tag[TAG_LEN]; /* секрет; нападник його НЕ бачить */
    oracle_mode mode;
    uint64_t    queries;      /* скільки кадрів нападник уже надіслав */
    uint32_t    noise_state;  /* стан генератора джитеру вимірювання */
    uint32_t    last_cost;    /* «час» останньої відповіді, умовні одиниці */
} oracle;

void oracle_init(oracle *o, const uint8_t tag[TAG_LEN], oracle_mode mode, uint32_t seed);

/* Надсилає приймачу кадр із тегом guess.
   Повертає 1, якщо приймач кадр ПРИЙНЯВ, і 0 інакше.
   Побічно оновлює last_cost — те, що нападник змірює ззовні. */
int oracle_ask(oracle *o, const uint8_t guess[TAG_LEN]);

uint32_t oracle_last_cost(const oracle *o);

/* Затирає секрет: ключі не лежать у пам'яті довше, ніж потрібні. */
void oracle_destroy(oracle *o);

#endif /* ORACLE_H */
