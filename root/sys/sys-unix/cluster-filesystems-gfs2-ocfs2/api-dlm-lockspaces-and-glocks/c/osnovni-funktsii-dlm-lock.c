#include <libdlm.h>
#include <stdio.h>
#include <string.h>

/* Базовий приклад підключення до простору блокувань та виклику dlm_ls_lock у C */
int acquire_cluster_lock(dlm_lshandle_t ls, const char *res_name, uint32_t mode,
                         struct dlm_lksb *lksb, void (*ast)(void *), void (*bast)(void *, int)) {
    int status = dlm_ls_lock(ls,
                             mode,
                             lksb,
                             DLM_LKF_NOQUEUE,
                             res_name,
                             strlen(res_name),
                             0,            /* parent lock id */
                             ast,
                             lksb,         /* ast argument */
                             bast,
                             lksb);        /* bast argument */
    return status;
}
