/* sedbuf.h — Pattern Space і Hold Space: пам'ять регістрів та команди над ними.
 *
 * Обидва регістри — неперервні байтові масиви на купі з єдиним інваріантом:
 * на позиції data[len] завжди лежить '\0'. Саме тому data можна віддавати
 * у regexec(), fputs() чи write() без проміжних копій. */
#ifndef SEDBUF_H
#define SEDBUF_H

#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

typedef struct {
    char  *data;   /* Покажчик на виділений блок пам'яті в купі */
    size_t len;    /* Поточна довжина без кінцевого нульового байта */
    size_t cap;    /* Місткість блоку разом із місцем під термінатор */
} SedBuffer;

typedef struct {
    SedBuffer pattern_space;  /* Основний робочий регістр */
    SedBuffer hold_space;     /* Допоміжний регістр збереження стану */
    size_t line_number;       /* Наскрізний лічильник записів */
    bool is_last_line;        /* Адреса $: наступне читання дасть EOF */
    bool deleted;             /* Рядок відкинуто командою d/D */
    bool subst_success;       /* Брудний біт успіху s/// для t і T */
} SedState;

/* Нестача пам'яті — не ситуація, з якої потоковий редактор виходить:
   GNU sed завершується кодом 4 (panic), робимо так само. */
void sed_fatal(const char *what);

void sedbuf_init(SedBuffer *b);
void sedbuf_free(SedBuffer *b);
/* Геометричний ріст 1.5x із вирівнюванням за 64 байтами: нарощування буфера
   лишається амортизовано константним. */
void sedbuf_reserve(SedBuffer *b, size_t need);
void sedbuf_assign(SedBuffer *b, const char *src, size_t len);
void sedbuf_append(SedBuffer *b, const char *src, size_t len);
void sedbuf_append_byte(SedBuffer *b, char c);
/* Обнуляє довжину, ємність лишає — це і є семантика команди z. */
void sedbuf_clear(SedBuffer *b);

void sed_state_init(SedState *st);
void sed_state_free(SedState *st);

void sed_hold(SedState *st);         /* h — Hold = Pattern */
void sed_hold_append(SedState *st);  /* H — Hold = Hold + '\n' + Pattern */
void sed_get(SedState *st);          /* g — Pattern = Hold */
void sed_get_append(SedState *st);   /* G — Pattern = Pattern + '\n' + Hold */
void sed_exchange(SedState *st);     /* x — обмін дескрипторами, строго O(1) */
void sed_zap(SedState *st);          /* z — очистити Pattern, не рвучи ланцюжок */
void sed_delete(SedState *st);       /* d — очистити Pattern і почати новий цикл */
/* D — зняти текст до першого '\n'. true: сценарій перезапускається з ip = 0
   над залишком буфера БЕЗ читання нового запису. */
bool sed_delete_first_line(SedState *st);

void sed_print(const SedState *st, FILE *out, int sep);            /* p */
void sed_print_first_line(const SedState *st, FILE *out, int sep); /* P */

/* Читання чергового запису з роздільником sep ('\n', або '\0' для -z).
   Роздільник у Pattern Space не потрапляє: через це '$' у регулярному виразі
   зіставляється з кінцем тексту, а не з переносом рядка. false — EOF. */
bool sed_read_record(SedState *st, FILE *in, int sep);

#endif /* SEDBUF_H */
