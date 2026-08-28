#define _GNU_SOURCE
#include <signal.h>
#include <ucontext.h>
#include <stdint.h>

static void recover(void);                  /* куди піти замість збою */

static volatile sig_atomic_t was_write;
static void *fault_at;
static void *fault_pc;

static void on_segv(int sig, siginfo_t *info, void *uc_raw)
{
    ucontext_t *uc = uc_raw;
    greg_t     *r  = uc->uc_mcontext.gregs;

    fault_at  = info->si_addr;               /* == (void *)r[REG_CR2] */
    fault_pc  = (void *)r[REG_RIP];          /* інструкція, що впала  */
    was_write = (r[REG_ERR] & 2) != 0;       /* біт 1 — це був запис  */

    r[REG_RIP] = (greg_t)(uintptr_t)recover; /* повернутися не сюди   */
}
