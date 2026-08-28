#include <linux/membarrier.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>

static int membarrier(int cmd, unsigned int flags, int cpu_id)
{
    return syscall(__NR_membarrier, cmd, flags, cpu_id);
}

int barrier_init(void)
{
    int mask = membarrier(MEMBARRIER_CMD_QUERY, 0, 0);
    if (mask < 0 || !(mask & MEMBARRIER_CMD_PRIVATE_EXPEDITED))
        return -1;                       /* ядро старе — потрібен запасний шлях */
    return membarrier(MEMBARRIER_CMD_REGISTER_PRIVATE_EXPEDITED, 0, 0);
}

void publish(struct route **slot, struct route *fresh)
{
    __atomic_store_n(slot, fresh, __ATOMIC_RELEASE);  /* нова таблиця видима */
    membarrier(MEMBARRIER_CMD_PRIVATE_EXPEDITED, 0, 0);
    /* тут кожен побратим уже пройшов свою точку:
       якщо його active[] читається як 0, він точно не тримає стару таблицю */
}
