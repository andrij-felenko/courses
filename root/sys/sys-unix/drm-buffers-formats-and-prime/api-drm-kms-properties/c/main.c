/* C: Ручне створення та звільнення об'єкта запиту */
#include <xf86drm.h>
#include <xf86drmMode.h>

drmModeAtomicReqPtr req = drmModeAtomicAlloc();
if (!req) {
    /* Помилка виділення пам'яті */
}

/* Використання запиту... */

drmModeAtomicFree(req);
