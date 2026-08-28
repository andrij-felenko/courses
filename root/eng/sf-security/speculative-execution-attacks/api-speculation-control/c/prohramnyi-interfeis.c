#include <stdio.h>
#include <errno.h>
#include <sys/prctl.h>

/* Блокування непрямої спекуляції та спекулятивного читання пам'яті */
int enable_process_isolation(void) {
    /* Незворотно блокуємо отруєння непрямих переходів (STIBP / IBPB) */
    if (prctl(PR_SET_SPECULATION_CTRL,
              PR_SPEC_INDIRECT_BRANCH,
              PR_SPEC_FORCE_DISABLE, 0, 0) != 0) {
        perror("prctl PR_SPEC_INDIRECT_BRANCH");
        return -1;
    }

    /* Забороняємо спекулятивний обхід черги збереження (SSBD) */
    if (prctl(PR_SET_SPECULATION_CTRL,
              PR_SPEC_STORE_BYPASS,
              PR_SPEC_FORCE_DISABLE, 0, 0) != 0) {
        perror("prctl PR_SPEC_STORE_BYPASS");
        return -1;
    }

    return 0;
}

/* Перевірка поточного статусу захищеності процесу */
int is_isolation_enforced(void) {
    int res = prctl(PR_GET_SPECULATION_CTRL, PR_SPEC_INDIRECT_BRANCH, 0, 0, 0);
    if (res < 0) {
        return -1;
    }
    /* Перевіряємо чи прапорець встановлено через prctl та зафіксовано незворотно */
    return (res & PR_SPEC_PRCTL) && (res & PR_SPEC_FORCE_DISABLE);
}
