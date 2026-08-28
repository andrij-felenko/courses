#include <stdio.h>

/* Статичне зв'язування: звичайна C-функція */
void static_render_circle(double radius) {
    (void)radius;
}

/* Динамічне зв'язування: виклик через покажчик на функцію */
typedef void (*draw_fn)(void *data);

void invoke_dynamic(draw_fn fn, void *data) {
    /* Непрямий виклик: процесор бере адресу з аргументу fn */
    fn(data);
}
