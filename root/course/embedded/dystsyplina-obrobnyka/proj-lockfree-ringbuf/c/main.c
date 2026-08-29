/* Демонстрація буфера в його рідному сценарії: приймач UART сипле байтами
   телеметрії з переривання, головний цикл збирає з них рядки.

   На мікроконтролері uart_rx_isr() викликають із USARTx_IRQHandler; тут його
   викликає імітатор потоку, бо предмет — дисципліна обміну, а не конкретний
   периферійний модуль. Три сцени: рівний потік, переповнення, режим
   «важливі лише найсвіжіші дані». */

#include "ringbuf.h"

#include <stdio.h>

static rb_t g_rx;   /* черга UART → головний цикл */

/* ---------------- сторона обробника переривання ---------------- */

static void uart_rx_isr(uint8_t byte) {
    /* Усе, що робить обробник: кладе байт і виходить. Ні друку, ні malloc,
       ні очікування. При переповненні лише зростає лічильник втрат. */
    (void)rb_push_isr(&g_rx, byte);
}

/* UART з апаратним FIFO віддає кілька байтів за одне переривання */
static void uart_rx_isr_fifo(const uint8_t *data, size_t len) {
    (void)rb_push_isr_burst(&g_rx, data, len);
}

/* ---------------- сторона головного циклу ---------------- */

#define LINE_MAX 32

typedef struct {
    char     text[LINE_MAX];
    size_t   len;
    bool     drop_to_eol;   /* рядок зіпсовано: дочитуємо до '\n' і викидаємо */
    unsigned lines;
    unsigned broken;
} line_reader_t;

static void line_reader_init(line_reader_t *lr) {
    lr->len = 0u;
    lr->drop_to_eol = false;
    lr->lines = 0u;
    lr->broken = 0u;
}

/* Після викидання найстарішого кадр рветься посеред рядка — треба
   синхронізуватися по роздільнику, а не показувати огризок. */
static void line_reader_resync(line_reader_t *lr) {
    lr->len = 0u;
    lr->drop_to_eol = true;
}

static void line_reader_feed(line_reader_t *lr, uint8_t byte) {
    if (byte == '\n') {
        if (lr->drop_to_eol) {
            lr->broken++;
        } else {
            lr->text[lr->len] = '\0';
            lr->lines++;
            printf("    рядок: %s\n", lr->text);
        }
        lr->len = 0u;
        lr->drop_to_eol = false;
        return;
    }
    if (lr->drop_to_eol) {
        return;
    }
    if (lr->len + 1u >= LINE_MAX) {
        lr->drop_to_eol = true;   /* довший за буфер — теж зіпсований кадр */
        return;
    }
    lr->text[lr->len++] = (char)byte;
}

static void drain(line_reader_t *lr) {
    uint8_t chunk[32];
    size_t  n;

    while ((n = rb_pop_burst(&g_rx, chunk, sizeof chunk)) != 0u) {
        for (size_t i = 0u; i < n; i++) {
            line_reader_feed(lr, chunk[i]);
        }
    }
}

/* ---------------- імітатор потоку ---------------- */

static size_t make_line(uint8_t *out, size_t cap, unsigned n) {
    const int written = snprintf((char *)out, cap, "T=%u.%u;H=%u\n",
                                 20u + n % 5u, n % 10u, 40u + n % 7u);
    return (written < 0 || (size_t)written >= cap) ? 0u : (size_t)written;
}

int main(void) {
    uint8_t       line[LINE_MAX];
    line_reader_t lr;

    rb_init(&g_rx);
    line_reader_init(&lr);

    printf("Місткість буфера: %zu байт (один слот під ознаку порожнечі)\n\n",
           rb_capacity());

    /* Сцена 1. Головний цикл встигає: між перериваннями він вичитує чергу,
       тож вона майже завжди порожня. */
    printf("[1] рівний потік\n");
    for (unsigned n = 0u; n < 4u; n++) {
        const size_t len = make_line(line, sizeof line, n);
        for (size_t i = 0u; i < len; i++) {
            uart_rx_isr(line[i]);
            drain(&lr);
        }
    }
    printf("    прийнято рядків: %u, втрачено байтів: %u\n\n",
           lr.lines, (unsigned)rb_dropped(&g_rx));

    /* Сцена 2. Головний цикл застряг у довгій роботі (запис у флеш, обчислення),
       а переривання сипле далі. Буфер повний, зайве втрачено — але жоден
       обробник не заблокувався й не зіпсував уже прийнятих даних. */
    printf("[2] споживач застряг, потік не спинився\n");
    const uint32_t before = rb_dropped(&g_rx);
    for (unsigned n = 0u; n < 30u; n++) {
        const size_t len = make_line(line, sizeof line, n);
        uart_rx_isr_fifo(line, len);   /* нікого не чекаємо */
    }
    printf("    у черзі: %zu байт, втрачено за сцену: %u\n",
           rb_available(&g_rx), (unsigned)(rb_dropped(&g_rx) - before));
    printf("    головний цикл ожив і вичитує:\n");
    drain(&lr);
    printf("    цілих рядків: %u, порваних: %u\n\n", lr.lines, lr.broken);

    /* Сцена 3. Дані, де цінні лише найсвіжіші (потік вимірювань). Замість
       чекати місця, споживач сам викидає старе: tail його, і рухати цей
       індекс він має право будь-коли. */
    printf("[3] важливі лише найсвіжіші дані\n");
    for (unsigned n = 100u; n < 130u; n++) {
        const size_t len = make_line(line, sizeof line, n);
        uart_rx_isr_fifo(line, len);
    }
    const size_t queued = rb_available(&g_rx);
    const size_t keep   = 40u;
    if (queued > keep) {
        const size_t dropped_old = rb_discard_oldest(&g_rx, queued - keep);
        line_reader_resync(&lr);
        printf("    викинуто найстаріших: %zu байт\n", dropped_old);
    }
    drain(&lr);

    printf("\nПідсумок: рядків %u, порваних %u, байтів втрачено в ISR %u\n",
           lr.lines, lr.broken, (unsigned)rb_dropped(&g_rx));
    return 0;
}
