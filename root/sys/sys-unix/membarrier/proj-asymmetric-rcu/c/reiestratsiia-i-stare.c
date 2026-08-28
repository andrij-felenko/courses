static int mode;                        /* 1 — експедований, 2 — глобальний, 0 — трюк */
static char *helper;

static int membarrier(int cmd, unsigned int flags, int cpu)
{ return syscall(__NR_membarrier, cmd, flags, cpu); }

int rcu_init(void)
{
    int mask = membarrier(MEMBARRIER_CMD_QUERY, 0, 0);

    if (mask > 0 && (mask & MEMBARRIER_CMD_PRIVATE_EXPEDITED) &&
        membarrier(MEMBARRIER_CMD_REGISTER_PRIVATE_EXPEDITED, 0, 0) == 0)
        return mode = 1;                /* одиниці-десятки мікросекунд */
    if (mask > 0 && (mask & MEMBARRIER_CMD_GLOBAL))
        return mode = 2;                /* десятки мілісекунд, зате без реєстрації */

    helper = mmap(NULL, 4096, PROT_READ | PROT_WRITE,
                  MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (helper == MAP_FAILED) return -1;
    *helper = 0;
    mlock(helper, 4096);                /* сторінка мусить лишатися присутньою */
    return mode = 0;
}

static void barrier_all(void)
{
    switch (mode) {
    case 1: membarrier(MEMBARRIER_CMD_PRIVATE_EXPEDITED, 0, 0); break;
    case 2: membarrier(MEMBARRIER_CMD_GLOBAL, 0, 0);            break;
    default:
        mprotect(helper, 4096, PROT_READ | PROT_WRITE);
        *(volatile char *)helper = 0;
        mprotect(helper, 4096, PROT_NONE);   /* звуження прав тягне розсилку IPI */
    }
}
