/* Прошивка, яка при старті звіряє сама себе з власними метаданими збірки
   й лишає вирок у діагностичній скриньці. Мінімум довкола: таблиця векторів,
   стартовий код і перевірка — усе, чого вимагає тема. */

#include "build_meta.h"

#include <stddef.h>
#include <stdint.h>

/* Символи розкладки з c/linker.ld */
extern uint32_t __data_load;
extern uint32_t __data_start;
extern uint32_t __data_end;
extern uint32_t __bss_start;
extern uint32_t __bss_end;
extern uint8_t  __image_start;
extern uint8_t  __image_end;
extern uint32_t _estack;

void Reset_Handler(void);
static void Default_Handler(void);
int main(void);

/* Скринька в .noinit: стартовий код її не чистить, тож вирок переживає
   теплий перезапуск і читається зневаджувачем або бутлоадером. */
typedef struct {
    uint32_t status;
    char     text[160];
} diag_block_t;

__attribute__((section(".noinit"), used))
volatile diag_block_t g_diag;

__attribute__((section(".vectors"), used))
void (*const g_vectors[])(void) = {
    (void (*)(void))(uintptr_t)&_estack, /* початкове значення SP */
    Reset_Handler,
    Default_Handler,  /* NMI */
    Default_Handler   /* HardFault */
};

static void Default_Handler(void)
{
    for (;;) {
        /* тут нема чого рятувати: зупиняємось, лишаючи стан для зневаджувача */
    }
}

void Reset_Handler(void)
{
    /* Перенесення ініціалізованих даних із Flash у RAM */
    const uint32_t *src = &__data_load;
    for (uint32_t *dst = &__data_start; dst < &__data_end; ++dst) {
        *dst = *src++;
    }
    /* Обнулення .bss; .noinit свідомо лишається недоторканим */
    for (uint32_t *dst = &__bss_start; dst < &__bss_end; ++dst) {
        *dst = 0U;
    }

    (void)main();

    for (;;) {
    }
}

int main(void)
{
    const uint8_t *const image = &__image_start;
    const uint32_t image_len = (uint32_t)(&__image_end - &__image_start);

    /* Метадані читаємо з Flash за адресою секції, а не через ім'я об'єкта */
    const fw_meta_t *const meta = fw_meta_current();
    const fw_meta_status_t status = fw_meta_verify(meta, image, image_len);

    /* Рядок звіту складаємо завжди: навіть при поганому CRC корисно бачити,
       який саме коміт і який тулчейн дали цей образ. */
    char line[sizeof g_diag.text];
    size_t n = fw_meta_report(line, sizeof line, meta);

    /* Дописуємо вирок у той самий рядок, лишаючи місце під нульовий байт */
    const char *reason = fw_meta_status_text(status);
    const char *tag = " status=";
    while (*tag != '\0' && n + 1U < sizeof line) {
        line[n++] = *tag++;
    }
    while (*reason != '\0' && n + 1U < sizeof line) {
        line[n++] = *reason++;
    }
    line[n] = '\0';

    g_diag.status = (uint32_t)status;
    for (size_t i = 0U; i < sizeof line; ++i) {
        g_diag.text[i] = (i <= n) ? line[i] : '\0';
    }

    if (status != FW_META_OK) {
        /* Далі керування не віддаємо: образ не той, за який себе видає.
           Вирок уже в скриньці — його прочитає бутлоадер або зневаджувач. */
        for (;;) {
        }
    }

    for (;;) {
        __asm__ volatile("wfi");
    }
}
