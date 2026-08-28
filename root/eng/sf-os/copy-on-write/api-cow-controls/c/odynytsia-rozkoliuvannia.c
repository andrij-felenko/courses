#include <sys/prctl.h>

prctl(PR_SET_THP_DISABLE, 1, 0, 0, 0);   /* з 3.15: вимкнути THP для процесу */
prctl(PR_GET_THP_DISABLE, 0, 0, 0, 0);   /* з 3.15: повертає 0 або 1 */

/* Вимкнути скрізь, окрім явно порадженого через madvise.
   УВАГА: прапорець набагато молодший за сам PR_SET_THP_DISABLE —
   він з'явився аж у ядрах кінця 2025 року. На всіх чинних LTS
   цей виклик поверне EINVAL. */
prctl(PR_SET_THP_DISABLE, 1, PR_THP_DISABLE_EXCEPT_ADVISED, 0, 0);
