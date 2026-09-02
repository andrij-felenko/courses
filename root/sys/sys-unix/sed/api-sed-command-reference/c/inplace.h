/* inplace.h — механіка sed -i: транзакційна підміна файла через тіньову копію.
 *
 * Відкрити файл на перезапис не можна: O_TRUNC знищив би ще не вичитані рядки.
 * Тому результат лягає в тимчасовий файл ПОРУЧ із ціллю (rename(2) не ходить
 * між точками монтування) і підмінює запис каталогу одним атомарним викликом. */
#ifndef INPLACE_H
#define INPLACE_H

#include <stdbool.h>
#include <stddef.h>

typedef struct {
    const char *backup_suffix;  /* NULL — без резервної копії (-i проти -i.bak) */
    bool follow_symlinks;       /* --follow-symlinks: правити ціль, а не саме посилання */
} SedInplaceOpts;

/* 0 — успіх; -1 — помилка, причина лишається в errno. */
int sed_inplace_commit(const char *target, const char *content, size_t len,
                       const SedInplaceOpts *opts);

#endif /* INPLACE_H */
