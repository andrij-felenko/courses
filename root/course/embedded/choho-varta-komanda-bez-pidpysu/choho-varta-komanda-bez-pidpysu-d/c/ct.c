#include "ct.h"

#include <string.h>

/*
 * Читаємо через volatile-вказівники навмисно.
 *
 * Без volatile компілятор має повне право помітити, що результат циклу
 * визначений уже на першому ненульовому diff, і зібрати з нього ранній
 * вихід — тобто рівно ту витікаючу поведінку memcmp, яку ми тут прибираємо.
 * Гарантії «мій gcc так не робить» не існує: наступна версія робить.
 */
int ct_verify(const uint8_t *a, const uint8_t *b, size_t len)
{
    const volatile uint8_t *va = (const volatile uint8_t *)a;
    const volatile uint8_t *vb = (const volatile uint8_t *)b;
    uint8_t diff = 0;
    size_t i;

    for (i = 0; i < len; ++i) {
        diff |= (uint8_t)(va[i] ^ vb[i]);
    }

    /* Згортаємо diff у 0/-1 без умовного переходу.
       Для будь-якого ненульового x вираз (x | -x) має одиницю в старшому
       біті; для x == 0 він дорівнює нулю. Далі зсув і зміна знака. */
    {
        uint8_t neg = (uint8_t)(0u - (unsigned)diff);
        uint8_t nonzero = (uint8_t)((diff | neg) >> 7);
        return -(int)nonzero;
    }
}

/*
 * Вказівник на memset оголошений volatile: виклик через нього компілятор
 * прибрати не може, бо не знає, що саме там лежить у момент виконання.
 * Це переносний відповідник explicit_bzero/memset_s.
 */
static void *(*const volatile ct_memset)(void *, int, size_t) = memset;

void ct_wipe(void *buf, size_t len)
{
    if (buf != NULL && len != 0u) {
        ct_memset(buf, 0, len);
    }
}
