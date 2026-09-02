/* ext_func_layout.h — витяг із <gawkapi.h>: дескриптор функції розширення й
 * протокол рукостискання. Теж цитата контракту, теж не для підключення поруч
 * із оригінальним заголовком.
 */
#ifndef AWK_EXT_FUNC_LAYOUT_H
#define AWK_EXT_FUNC_LAYOUT_H

#include "value_layout.h"

/* Версії API. Старша мусить збігтися точно (від неї залежить розкладка
   структур), молодша в інтерпретатора — бути не меншою за нашу. */
#define GAWK_API_MAJOR_VERSION 4
#define GAWK_API_MINOR_VERSION 0

typedef void *awk_ext_id_t;   /* дескриптор самого розширення */

typedef struct awk_ext_func {
    const char *name;         /* під цим ім'ям функція з'явиться в AWK */

    /* num_actual_args — скільки аргументів передано ФАКТИЧНО (AWK дозволяє
       менше за max); result — куди писати повернене значення, його ж і
       повертаємо; finfo — цей самий дескриптор, звідси беруть .data. */
    awk_value_t *(*const function)(int num_actual_args,
                                   awk_value_t *result,
                                   struct awk_ext_func *finfo);

    const unsigned short max_expected_args;  /* більше — попередження lint */
    const unsigned short min_required_args;  /* менше — фатальна помилка */
    awk_bool_t suppress_lint;
    void *data;               /* стан модуля: те, що в C++ було б this */
} awk_ext_func_t;

/* Точка входу. Викликається один раз після dlopen(3):
     1) перевірити версії API і повернути 0, якщо не збігаються;
     2) зареєструвати кожну функцію через add_ext_func();
     3) повернути 1.
   Поруч мусить бути ВИЗНАЧЕНИЙ символ plugin_is_GPL_compatible, інакше
   gawk відмовиться завантажувати бібліотеку. */
extern int dl_load(const struct gawk_api *const api_p, awk_ext_id_t id);
extern int plugin_is_GPL_compatible;

/* Найчастіша помилка заповнення таблиці — переставлені місцями max і min:
   компілятор мовчить, а gawk починає вимагати аргументів більше, ніж
   функція взагалі здатна прийняти. */
static inline int awk_ext_func_is_sane(const awk_ext_func_t *f)
{
    return f != NULL
        && f->name != NULL && f->name[0] != '\0'
        && f->function != NULL
        && f->min_required_args <= f->max_expected_args;
}

#endif /* AWK_EXT_FUNC_LAYOUT_H */
