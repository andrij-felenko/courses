/* syscalls.c — місток між стандартною бібліотекою C (newlib) і голим залізом.

   Бібліотека написана в припущенні, що під нею є операційна система: malloc
   просить пам'ять у ядра через _sbrk, printf пише у файловий дескриптор через
   _write. Операційної системи тут немає, тому ці функції пише сама прошивка.
   Контракт задано newlib, і міняти в ньому не можна нічого: ні імена, ні
   підписи, ні значення відмови (void *)-1, ні код у errno.

   Головна з них — _sbrk. Купа росте від символу _end, тобто від першого
   вільного байта за глобальними змінними, угору назустріч стеку, який росте
   від _estack униз. Ця зустріч і є єдина справжня небезпека, тому стеля
   перевіряється двічі: статично за резервом _Min_Stack_Size і динамічно за
   поточним значенням покажчика стека. */

#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include "cortex_m.h"
#include "startup.h"

/* Прототипи: newlib кличе ці функції за іменем, тож без явних оголошень
   компілятор із -Wmissing-prototypes справедливо лається. */
void *_sbrk(ptrdiff_t incr);
int _write(int file, char *ptr, int len);
int _read(int file, char *ptr, int len);
int _close(int file);
int _fstat(int file, struct stat *st);
int _isatty(int file);
int _lseek(int file, int offset, int whence);
int _getpid(void);
int _kill(int pid, int sig);
void _exit(int status) __attribute__((noreturn));

/* Поточна вершина купи. Лежить у .bss, тож на момент першого malloc уже
   занулена стартовим кодом — саме тому нуль надійно означає «ще не почато». */
static uint8_t *s_heap_top;

/* Запас, який лишаємо стеку понад те, що він з'їв просто зараз. Найглибший
   ланцюг викликів прошивки має вміститися в цей зазор. */
#define HEAP_STACK_GUARD 256U

/* Статична стеля: кінець RAM мінус резерв, який лінкер уже перевірив на етапі
   збирання. Символ _Min_Stack_Size не має секції, тож його АДРЕСА і є число. */
static uint8_t *static_ceiling(void)
{
    const uintptr_t top     = (uintptr_t)&_estack;
    const uintptr_t reserve = (uintptr_t)&_Min_Stack_Size;
    return (uint8_t *)(top - reserve);
}

/* Динамічна стеля: куди справді доріс стек просто зараз, мінус зазор.
   Статичний резерв каже, скільки стека ГАРАНТОВАНО, а ця перевірка ловить
   випадок, коли рекурсія вже з'їла більше за резерв. */
static uint8_t *dynamic_ceiling(void)
{
    const uintptr_t sp = cm_get_msp();
    if (sp < HEAP_STACK_GUARD) {
        return (uint8_t *)0;
    }
    return (uint8_t *)(sp - HEAP_STACK_GUARD);
}

void *_sbrk(ptrdiff_t incr)
{
    if (s_heap_top == NULL) {
        s_heap_top = (uint8_t *)&_end;
    }

    uint8_t *const floor = (uint8_t *)&_end;
    uint8_t *ceiling = static_ceiling();
    uint8_t *const dynamic = dynamic_ceiling();
    if (dynamic < ceiling) {
        ceiling = dynamic;   /* беремо нижчу з двох стель */
    }

    /* Повернення пам'яті newlib робить від'ємним приростом. Нижче за _end
       опускатися не можна: там лежать глобальні змінні. */
    if (incr < 0) {
        const size_t back = (size_t)(-(intptr_t)incr);
        if ((size_t)(s_heap_top - floor) < back) {
            errno = EINVAL;
            return (void *)-1;
        }
    } else {
        /* Порівнюємо ЗАЛИШОК, а не суму: s_heap_top + incr переповнилося б
           мовчки, і перевірка пропустила б завідомо завеликий запит. */
        if (ceiling <= s_heap_top ||
            (uintptr_t)(ceiling - s_heap_top) < (uintptr_t)incr) {
            errno = ENOMEM;
            return (void *)-1;   /* саме це значення newlib читає як відмову */
        }
    }

    uint8_t *const previous = s_heap_top;
    s_heap_top += incr;
    return previous;
}

/* ── Вивід через ITM: printf працює під налагоджувачем без жодного UART ─────
   Порт 0 модуля трасування. Пишемо лише тоді, коли налагоджувач увімкнув
   трасування (TRCENA + дозвіл порту): інакше цикл очікування готовності
   крутився б вічно. */
#define DEMCR      0xE000EDFCU
#define DEMCR_TRCENA (1U << 24)
#define ITM_STIM0  0xE0000000U
#define ITM_TER    0xE0000E00U
#define ITM_TCR    0xE0000E80U
#define ITM_TCR_ITMENA (1U << 0)

static int itm_enabled(void)
{
    return (CM_REG32(DEMCR) & DEMCR_TRCENA) &&
           (CM_REG32(ITM_TCR) & ITM_TCR_ITMENA) &&
           (CM_REG32(ITM_TER) & 1U);
}

static void itm_putc(char c)
{
    while (CM_REG32(ITM_STIM0) == 0U) {
        /* порт зайнятий попереднім символом */
    }
    CM_REG32(ITM_STIM0) = (uint32_t)(uint8_t)c;
}

int _write(int file, char *ptr, int len)
{
    if ((file != STDOUT_FILENO) && (file != STDERR_FILENO)) {
        errno = EBADF;
        return -1;
    }
    if ((ptr == NULL) || (len < 0)) {
        errno = EINVAL;
        return -1;
    }
    if (itm_enabled()) {
        for (int i = 0; i < len; ++i) {
            itm_putc(ptr[i]);
        }
    }
    /* Байти вважаємо прийнятими навіть без слухача: інакше printf у прошивці
       без налагоджувача повертав би помилку й ламав прикладну логіку. */
    return len;
}

/* Вхідного потоку немає: одразу кінець файлу. */
int _read(int file, char *ptr, int len)
{
    (void)file; (void)ptr; (void)len;
    return 0;
}

int _close(int file)
{
    (void)file;
    errno = EBADF;
    return -1;
}

/* newlib питає тип дескриптора, щоб обрати режим буферизації. Символьний
   пристрій означає «без буфера» — саме те, що треба для трасування. */
int _fstat(int file, struct stat *st)
{
    (void)file;
    if (st == NULL) {
        errno = EINVAL;
        return -1;
    }
    st->st_mode = S_IFCHR;
    return 0;
}

int _isatty(int file)
{
    (void)file;
    return 1;
}

int _lseek(int file, int offset, int whence)
{
    (void)file; (void)offset; (void)whence;
    return 0;   /* потік без позиції: завжди початок */
}

int _getpid(void)
{
    return 1;
}

int _kill(int pid, int sig)
{
    (void)pid; (void)sig;
    errno = EINVAL;
    return -1;
}

/* Сюди потрапляє abort() і провалений assert(). Виходити нікуди, тож
   спиняємося так само, як термінальна пастка стартового коду. */
void _exit(int status)
{
    (void)status;
    cm_bkpt();
    for (;;) {
        cm_wfi();
    }
}
